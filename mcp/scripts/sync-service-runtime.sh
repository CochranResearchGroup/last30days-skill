#!/usr/bin/env bash
# Stage the independent service artifact and its managed lifecycle controls.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${MCP_DIR}/.." && pwd)"
RUNTIME_DIR="${MCP_DIR}/runtime"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --repo-root)
      REPO_ROOT="$(cd "$2" && pwd)"
      shift 2
      ;;
    --runtime-dir)
      mkdir -p "$2"
      RUNTIME_DIR="$(cd "$2" && pwd)"
      shift 2
      ;;
    *)
      echo "sync-service-runtime: unsupported argument: $1" >&2
      exit 2
      ;;
  esac
done

if [ ! -x "${REPO_ROOT}/service/scripts/build-runtime.sh" ] ||
  [ ! -f "${REPO_ROOT}/service/scripts/install.sh" ] ||
  [ ! -f "${REPO_ROOT}/service/systemd/last30days.service.in" ]; then
  echo "sync-service-runtime: independent service controls are incomplete" >&2
  exit 1
fi

case "${RUNTIME_DIR}" in
  ""|"/")
    echo "sync-service-runtime: unsafe runtime destination" >&2
    exit 1
    ;;
esac

STAGING_DIR="$(mktemp -d)"
trap 'find "${STAGING_DIR}" -depth -delete 2>/dev/null || true' EXIT
STAGED_SERVICE="${STAGING_DIR}/service"
mkdir -p \
  "${STAGED_SERVICE}/artifacts" \
  "${STAGED_SERVICE}/scripts" \
  "${STAGED_SERVICE}/systemd"

SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}" \
  bash "${REPO_ROOT}/service/scripts/build-runtime.sh" \
  --repo-root "${REPO_ROOT}" \
  --output-dir "${STAGED_SERVICE}/artifacts"
cp "${REPO_ROOT}/service/VERSION" "${STAGED_SERVICE}/VERSION"
cp "${REPO_ROOT}/service/scripts/install.sh" \
  "${STAGED_SERVICE}/scripts/install.sh"
cp "${REPO_ROOT}/service/systemd/last30days.service.in" \
  "${STAGED_SERVICE}/systemd/last30days.service.in"
chmod 0755 "${STAGED_SERVICE}/scripts/install.sh"

mkdir -p "${RUNTIME_DIR}"
find "${RUNTIME_DIR}" -mindepth 1 -delete
cp -R "${STAGED_SERVICE}" "${RUNTIME_DIR}/service"

echo "sync-service-runtime: staged independent service payload at ${RUNTIME_DIR}/service"
