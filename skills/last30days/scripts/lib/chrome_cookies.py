"""Chromium-family cookie extraction for macOS and Linux.

Extracts cookies from Chromium-based browser SQLite databases using only
stdlib modules and the system openssl CLI. Zero pip dependencies.

Chromium on macOS uses v10 encryption (AES-128-CBC with Keychain-stored key).
Every Chromium-based browser (Chrome, Brave, Edge, Vivaldi, Opera, Arc,
Chromium) shares the same algorithm; only the profile directory and Keychain
service name differ, so they all run through the same decryption core.

Chromium on Linux also uses the same v10 AES-128-CBC cookie format. The key is
read from libsecret through ``secret-tool`` when available, then falls back to
Chromium's historical local passphrase (``peanuts``). This is enough for local
agent auth on common desktop and headless Linux profiles without adding a
Python keyring dependency.
This is NOT affected by Windows App-Bound Encryption (v20).
"""

import hashlib
import logging
import os
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _lock_temp_cookie_copy(path: str) -> None:
    """Restrict copied cookie DB temp files to the current user on POSIX."""
    if os.name == "nt":
        return
    Path(path).chmod(0o600)

# Cookie DB locations
_APP_SUPPORT = Path.home() / "Library" / "Application Support"
_LINUX_CONFIG = Path.home() / ".config"
CHROME_BASE_DIR = _APP_SUPPORT / "Google" / "Chrome"
# Kept for backward compatibility; resolution now goes through the profile
# finder (which also handles the modern Network/Cookies layout).
CHROME_COOKIES_DB = CHROME_BASE_DIR / "Default" / "Cookies"
BRAVE_BASE_DIR = _APP_SUPPORT / "BraveSoftware" / "Brave-Browser"
CHROME_LINUX_BASE_DIR = _LINUX_CONFIG / "google-chrome"
BRAVE_LINUX_BASE_DIR = _LINUX_CONFIG / "BraveSoftware" / "Brave-Browser"

# Other Chromium-based browsers, keyed by FROM_BROWSER name. Each maps to
# (profile base directory, macOS Keychain service name). Chrome and Brave keep
# their dedicated helpers below for backward compatibility; everything here is
# resolved generically by extract_chromium_browser_cookies_macos(). Keychain
# service names follow Chromium's "<Browser> Safe Storage" convention.
CHROMIUM_BROWSER_PROFILES: dict[str, tuple[Path, str]] = {
    "edge": (_APP_SUPPORT / "Microsoft Edge", "Microsoft Edge Safe Storage"),
    "vivaldi": (_APP_SUPPORT / "Vivaldi", "Vivaldi Safe Storage"),
    "opera": (_APP_SUPPORT / "com.operasoftware.Opera", "Opera Safe Storage"),
    "arc": (_APP_SUPPORT / "Arc" / "User Data", "Arc Safe Storage"),
    "chromium": (_APP_SUPPORT / "Chromium", "Chromium Safe Storage"),
}

CHROMIUM_LINUX_BROWSER_PROFILES: dict[str, tuple[Path, str, tuple[str, ...]]] = {
    "edge": (
        _LINUX_CONFIG / "microsoft-edge",
        "Microsoft Edge",
        ("edge", "microsoft-edge", "Microsoft Edge"),
    ),
    "vivaldi": (
        _LINUX_CONFIG / "vivaldi",
        "Vivaldi",
        ("vivaldi", "Vivaldi"),
    ),
    "opera": (
        _LINUX_CONFIG / "opera",
        "Opera",
        ("opera", "Opera"),
    ),
    "chromium": (
        _LINUX_CONFIG / "chromium",
        "Chromium",
        ("chromium", "Chromium"),
    ),
}

# Chromium v10 encryption constants (shared by Chrome and Brave)
CHROME_SALT = b"saltysalt"
CHROME_PBKDF2_ITERATIONS = 1003
CHROME_LINUX_PBKDF2_ITERATIONS = 1
CHROME_KEY_LENGTH = 16
CHROME_LINUX_FALLBACK_PASSPHRASE = b"peanuts"
# IV is 16 space characters (0x20)
CHROME_IV_HEX = "20" * 16


def _get_chromium_encryption_key(service_name: str) -> Optional[bytes]:
    """Retrieve the encryption passphrase for a Chromium-based browser from macOS Keychain.

    Calls `security find-generic-password` which may trigger a system dialog
    on first access.

    Returns the raw passphrase bytes, or None on failure.
    """
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", service_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            logger.info("%s Keychain access denied or browser not installed: %s", service_name, result.stderr.strip())
            return None
        passphrase = result.stdout.strip()
        if not passphrase:
            logger.info("%s Keychain returned empty passphrase", service_name)
            return None
        return passphrase.encode("utf-8")
    except FileNotFoundError:
        logger.info("'security' command not found — not on macOS?")
        return None
    except subprocess.TimeoutExpired:
        logger.info("%s Keychain access timed out", service_name)
        return None
    except Exception as e:
        logger.info("Failed to get %s encryption key: %s", service_name, e)
        return None


def _get_chrome_encryption_key() -> Optional[bytes]:
    return _get_chromium_encryption_key("Chrome Safe Storage")


def _derive_aes_key(passphrase: bytes, iterations: int = CHROME_PBKDF2_ITERATIONS) -> bytes:
    """Derive 16-byte AES key from Chrome's Keychain passphrase via PBKDF2."""
    return hashlib.pbkdf2_hmac(
        "sha1",
        passphrase,
        CHROME_SALT,
        iterations,
        dklen=CHROME_KEY_LENGTH,
    )


def _decrypt_v10_value(encrypted_value: bytes, aes_key: bytes, db_version: int) -> Optional[str]:
    """Decrypt a Chrome v10-encrypted cookie value.

    Uses system openssl CLI for AES-128-CBC decryption (zero pip deps).
    For Chrome 130+ (db_version >= 24), strips 32-byte SHA-256 prefix after decryption.

    Returns decrypted string or None on failure.
    """
    # Strip the 'v10' prefix
    ciphertext = encrypted_value[3:]
    if not ciphertext:
        return None

    hex_key = aes_key.hex()

    try:
        result = subprocess.run(
            [
                "openssl", "enc", "-aes-128-cbc", "-d",
                "-K", hex_key,
                "-iv", CHROME_IV_HEX,
                "-nopad",
            ],
            input=ciphertext,
            capture_output=True,
            timeout=5,
        )
        if result.returncode != 0:
            logger.debug("openssl decryption failed: %s", result.stderr.decode(errors="replace").strip())
            return None

        decrypted = result.stdout
        if not decrypted:
            return None

        # Remove PKCS7 padding
        decrypted = _remove_pkcs7_padding(decrypted)
        if decrypted is None:
            return None

        # Chrome 130+ (db version >= 24): strip 32-byte SHA-256 prefix
        if db_version >= 24 and len(decrypted) > 32:
            decrypted = decrypted[32:]

        return decrypted.decode("utf-8", errors="replace")

    except FileNotFoundError:
        logger.info("openssl not found — cannot decrypt Chrome cookies")
        return None
    except subprocess.TimeoutExpired:
        logger.info("openssl decryption timed out")
        return None
    except Exception as e:
        logger.debug("Chrome cookie decryption error: %s", e)
        return None


def _remove_pkcs7_padding(data: bytes) -> Optional[bytes]:
    """Remove PKCS7 padding from decrypted data.

    The last byte indicates the number of padding bytes added.
    All padding bytes must have the same value.

    Returns unpadded data or None if padding is invalid.
    """
    if not data:
        return None
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        return None
    # Verify all padding bytes match
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        return None
    return data[:-pad_len]


def _get_db_version(cursor: sqlite3.Cursor) -> int:
    """Get Chrome cookie database version from the meta table.

    Returns 0 if meta table doesn't exist or version can't be read.
    """
    try:
        cursor.execute("SELECT value FROM meta WHERE key = 'version'")
        row = cursor.fetchone()
        if row:
            return int(row[0])
    except Exception:
        pass
    return 0


def _extract_chromium_cookies_from_db(
    db_path: Path,
    source_name: str,
    domain: str,
    cookie_names: list[str],
    get_aes_key,
) -> Optional[dict[str, str]]:
    """Extract cookies from a Chromium Cookies SQLite database.

    Copies the locked Cookies database to a temp file, reads specified cookies,
    and decrypts v10-encrypted values using a lazily resolved AES key.

    Args:
        db_path: Path to the browser's Cookies SQLite file.
        source_name: Human-readable browser/source name for logs.
        domain: Cookie domain to match (e.g., ".twitter.com", ".x.com").
        cookie_names: List of cookie names to extract.
        get_aes_key: Zero-arg callable returning a 16-byte AES key or None.

    Returns:
        Dict mapping cookie name to decrypted value, or None on failure.
        Only includes cookies that were successfully found and decrypted.
    """
    if not db_path.exists():
        logger.info("%s cookies database not found at %s", source_name, db_path)
        return None

    # Copy DB to temp file (browser locks the original while running)
    tmp_fd = None
    tmp_path = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".sqlite")
        shutil.copy2(str(db_path), tmp_path)
        _lock_temp_cookie_copy(tmp_path)
    except Exception as e:
        logger.info("Failed to copy %s cookies database: %s", source_name, e)
        if tmp_path:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
        return None
    finally:
        if tmp_fd is not None:
            import os
            os.close(tmp_fd)

    try:
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()

        db_version = _get_db_version(cursor)
        logger.debug("%s cookie DB version: %d", source_name, db_version)

        placeholders = ",".join("?" for _ in cookie_names)
        query = (
            f"SELECT name, value, encrypted_value FROM cookies "
            f"WHERE host_key LIKE ? AND name IN ({placeholders})"
        )
        params = [f"%{domain}"] + list(cookie_names)
        cursor.execute(query, params)

        results: dict[str, str] = {}
        aes_key = None
        key_fetched = False
        for name, value, encrypted_value in cursor.fetchall():
            if value:
                results[name] = value
                continue

            if encrypted_value and encrypted_value[:3] in (b"v10", b"v11"):
                if not key_fetched:
                    # Resolve the platform key lazily — only once we actually
                    # have an encrypted cookie to decrypt. This avoids macOS
                    # Keychain prompts and Linux keyring calls for browsers
                    # that don't hold the requested cookie.
                    aes_key = get_aes_key()
                    key_fetched = True
                if aes_key is None:
                    logger.debug("Skipping encrypted cookie %s — no %s key", name, source_name)
                    continue
                decrypted = _decrypt_v10_value(encrypted_value, aes_key, db_version)
                if decrypted:
                    results[name] = decrypted
                else:
                    logger.debug("Failed to decrypt cookie %s", name)
            elif encrypted_value:
                logger.debug("Unknown encryption for cookie %s (prefix: %r)", name, encrypted_value[:3])

        conn.close()

        if not results:
            logger.info("No matching cookies found in %s for domain %s", source_name, domain)
            return None

        return results

    except sqlite3.Error as e:
        logger.info("Failed to read %s cookies database: %s", source_name, e)
        return None
    except Exception as e:
        logger.info("Unexpected error reading %s cookies: %s", source_name, e)
        return None
    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass


def _extract_chromium_cookies_macos(
    db_path: Path,
    keychain_service: str,
    domain: str,
    cookie_names: list[str],
) -> Optional[dict[str, str]]:
    """Extract cookies from any Chromium-based browser on macOS."""

    def get_aes_key() -> Optional[bytes]:
        passphrase = _get_chromium_encryption_key(keychain_service)
        return _derive_aes_key(passphrase) if passphrase else None

    return _extract_chromium_cookies_from_db(
        db_path,
        keychain_service,
        domain,
        cookie_names,
        get_aes_key,
    )


def extract_chrome_cookies_macos(domain: str, cookie_names: list[str]) -> Optional[dict[str, str]]:
    """Extract cookies from Chrome on macOS.

    Resolves the cookie DB through the shared profile finder so Chrome gets the
    same modern ``Default/Network/Cookies`` (Chromium >= 96) and legacy
    ``Default/Cookies`` probing as the rest of the Chromium family.
    """
    db_path = _find_chromium_cookies_db(CHROME_BASE_DIR)
    if db_path is None:
        logger.info("Chrome cookies database not found under %s", CHROME_BASE_DIR)
        return None
    return _extract_chromium_cookies_macos(
        db_path, "Chrome Safe Storage", domain, cookie_names
    )


def _get_chromium_linux_passphrase(app_names: tuple[str, ...]) -> Optional[bytes]:
    """Return a Chromium Linux cookie passphrase from libsecret, if available."""
    secret_tool = shutil.which("secret-tool")
    if not secret_tool:
        return None

    for app_name in app_names:
        try:
            result = subprocess.run(
                [secret_tool, "lookup", "application", app_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except FileNotFoundError:
            return None
        except subprocess.TimeoutExpired:
            logger.info("secret-tool lookup timed out for %s", app_name)
            continue
        except Exception as exc:
            logger.debug("secret-tool lookup failed for %s: %s", app_name, exc)
            continue

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().encode("utf-8")
        if result.returncode not in (0, 1):
            logger.debug(
                "secret-tool lookup for %s exited %s: %s",
                app_name,
                result.returncode,
                result.stderr.strip(),
            )

    return None


def _linux_aes_key(app_names: tuple[str, ...]) -> bytes:
    """Derive the Linux Chromium AES key from keyring or local fallback."""
    passphrase = _get_chromium_linux_passphrase(app_names)
    if not passphrase:
        passphrase = CHROME_LINUX_FALLBACK_PASSPHRASE
    return _derive_aes_key(passphrase, iterations=CHROME_LINUX_PBKDF2_ITERATIONS)


def _extract_chromium_cookies_linux(
    db_path: Path,
    source_name: str,
    app_names: tuple[str, ...],
    domain: str,
    cookie_names: list[str],
) -> Optional[dict[str, str]]:
    """Extract cookies from any Chromium-based browser on Linux."""
    return _extract_chromium_cookies_from_db(
        db_path,
        source_name,
        domain,
        cookie_names,
        lambda: _linux_aes_key(app_names),
    )


def extract_chrome_cookies_linux(domain: str, cookie_names: list[str]) -> Optional[dict[str, str]]:
    """Extract cookies from Google Chrome on Linux."""
    db_path = _find_chromium_cookies_db(CHROME_LINUX_BASE_DIR)
    if db_path is None:
        logger.info("Chrome cookies database not found under %s", CHROME_LINUX_BASE_DIR)
        return None
    return _extract_chromium_cookies_linux(
        db_path,
        "Chrome",
        ("chrome", "google-chrome", "Chrome"),
        domain,
        cookie_names,
    )


def _profile_cookie_db(profile_dir: Path) -> Optional[Path]:
    """Return the Cookies DB inside a profile dir, or None.

    Prefers the modern ``Network/Cookies`` location (Chromium >= 96 moved the
    cookie store into a per-profile ``Network/`` subdirectory) and falls back
    to the legacy flat ``Cookies`` file. Different browsers and versions use
    different layouts, so both are probed.
    """
    for rel in ("Network/Cookies", "Cookies"):
        candidate = profile_dir / rel
        if candidate.exists():
            return candidate
    return None


def _find_chromium_cookies_db(base_dir: Path) -> Optional[Path]:
    """Find a Chromium-based browser's Cookies database under base_dir.

    Checks the Default profile first, then the base dir itself (Opera's flat
    layout), then numbered "Profile N" directories by most-recently-modified.
    Each location is probed for both the modern ``Network/Cookies`` and legacy
    ``Cookies`` paths (see _profile_cookie_db). Chromium browsers create extra
    profiles as "Profile 1", "Profile 2", etc. alongside Default; the most
    recently used one is the likeliest to hold current cookies. Lexicographic
    sort would visit "Profile 10" before "Profile 2", which can return the
    wrong profile, so we sort by mtime.
    """
    found = _profile_cookie_db(base_dir / "Default")
    if found:
        return found

    found = _profile_cookie_db(base_dir)
    if found:
        return found

    try:
        candidates = [
            child for child in base_dir.iterdir()
            if child.is_dir() and child.name.startswith("Profile ")
        ]
        for child in sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True):
            found = _profile_cookie_db(child)
            if found:
                return found
    except OSError:
        pass

    return None


def _find_brave_cookies_db() -> Optional[Path]:
    """Find Brave's Cookies database on macOS (Default, then Profile N)."""
    return _find_chromium_cookies_db(BRAVE_BASE_DIR)


def extract_brave_cookies_macos(domain: str, cookie_names: list[str]) -> Optional[dict[str, str]]:
    """Extract cookies from Brave on macOS.

    Brave uses the same v10 AES-128-CBC encryption as Chrome; only the DB
    path and Keychain service name differ.
    """
    db_path = _find_brave_cookies_db()
    if db_path is None:
        logger.info("Brave cookies database not found under %s", BRAVE_BASE_DIR)
        return None
    return _extract_chromium_cookies_macos(db_path, "Brave Safe Storage", domain, cookie_names)


def extract_brave_cookies_linux(domain: str, cookie_names: list[str]) -> Optional[dict[str, str]]:
    """Extract cookies from Brave on Linux."""
    db_path = _find_chromium_cookies_db(BRAVE_LINUX_BASE_DIR)
    if db_path is None:
        logger.info("Brave cookies database not found under %s", BRAVE_LINUX_BASE_DIR)
        return None
    return _extract_chromium_cookies_linux(
        db_path,
        "Brave",
        ("brave", "brave-browser", "Brave"),
        domain,
        cookie_names,
    )


def extract_chromium_browser_cookies_macos(
    browser: str, domain: str, cookie_names: list[str]
) -> Optional[dict[str, str]]:
    """Extract cookies from a registry-defined Chromium browser on macOS.

    Covers every browser in CHROMIUM_BROWSER_PROFILES (Edge, Vivaldi, Opera,
    Arc, Chromium). They all reuse Chrome's v10 AES-128-CBC encryption; only
    the profile directory and Keychain service name differ.
    """
    spec = CHROMIUM_BROWSER_PROFILES.get(browser)
    if spec is None:
        logger.debug("Unknown Chromium browser: %s", browser)
        return None
    base_dir, keychain_service = spec
    db_path = _find_chromium_cookies_db(base_dir)
    if db_path is None:
        logger.info("%s cookies database not found under %s", keychain_service, base_dir)
        return None
    return _extract_chromium_cookies_macos(db_path, keychain_service, domain, cookie_names)


def extract_chromium_browser_cookies_linux(
    browser: str, domain: str, cookie_names: list[str]
) -> Optional[dict[str, str]]:
    """Extract cookies from a registry-defined Chromium browser on Linux."""
    spec = CHROMIUM_LINUX_BROWSER_PROFILES.get(browser)
    if spec is None:
        logger.debug("Unknown Linux Chromium browser: %s", browser)
        return None
    base_dir, source_name, app_names = spec
    db_path = _find_chromium_cookies_db(base_dir)
    if db_path is None:
        logger.info("%s cookies database not found under %s", source_name, base_dir)
        return None
    return _extract_chromium_cookies_linux(
        db_path,
        source_name,
        app_names,
        domain,
        cookie_names,
    )
