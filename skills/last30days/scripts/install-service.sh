#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_SCRIPT="${SCRIPT_DIR}/service.py"
PYTHON_BIN="${LAST30DAYS_PYTHON:-$(command -v python3)}"
UNIT_NAME="last30days.service"
UNIT_DIR="${XDG_CONFIG_HOME:-${HOME}/.config}/systemd/user"
UNIT_PATH="${UNIT_DIR}/${UNIT_NAME}"

render_unit() {
  cat <<EOF
[Unit]
Description=last30days user-scoped intelligence service
After=network-online.target

[Service]
Type=simple
ExecStart="${PYTHON_BIN}" "${SERVICE_SCRIPT}" serve
Restart=on-failure
RestartSec=2
Environment=PATH=%h/.local/bin:%h/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/bin:/usr/local/bin:/usr/bin:/bin
UMask=0077
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=default.target
EOF
}

if [[ "${1:-}" == "--print-unit" ]]; then
  render_unit
  exit 0
fi

if ! "${PYTHON_BIN}" -c 'import sys; raise SystemExit(sys.version_info < (3, 12))'; then
  echo "last30days service requires Python 3.12+" >&2
  exit 2
fi
if [[ ! -f "${SERVICE_SCRIPT}" ]]; then
  echo "service runtime not found: ${SERVICE_SCRIPT}" >&2
  exit 2
fi
if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl is required for the Linux user-service installer" >&2
  exit 2
fi

mkdir -p "${UNIT_DIR}"
tmp_unit="$(mktemp "${UNIT_DIR}/.${UNIT_NAME}.XXXXXX")"
trap 'rm -f -- "${tmp_unit}"' EXIT
render_unit >"${tmp_unit}"
chmod 600 "${tmp_unit}"
mv -f -- "${tmp_unit}" "${UNIT_PATH}"
trap - EXIT

systemctl --user daemon-reload
systemctl --user enable "${UNIT_NAME}"
systemctl --user restart "${UNIT_NAME}"
systemctl --user --no-pager --full status "${UNIT_NAME}"
