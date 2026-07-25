#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
MCP_ROOT="${REPO_ROOT}/mcp"
INSTALL_ROOT="${XDG_BIN_HOME:-${HOME}/.local/bin}"
DESTINATION="${INSTALL_ROOT}/last30days-pp-mcp"
SOCKET_PATH="${LAST30DAYS_SERVICE_SOCKET:-${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/last30days/service.sock}"

if ! command -v go >/dev/null 2>&1; then
  echo "go is required to build the last30days MCP adapter" >&2
  exit 2
fi
if ! command -v codex >/dev/null 2>&1; then
  echo "codex is required to register the MCP adapter" >&2
  exit 2
fi

mkdir -p "${INSTALL_ROOT}"
tmp_binary="$(mktemp "${INSTALL_ROOT}/.last30days-pp-mcp.XXXXXX")"
trap 'rm -f -- "${tmp_binary}"' EXIT
(
  cd "${MCP_ROOT}"
  go build -trimpath -o "${tmp_binary}" ./cmd/last30days-pp-mcp
)
chmod 755 "${tmp_binary}"
mv -f -- "${tmp_binary}" "${DESTINATION}"
trap - EXIT

if codex mcp get last30days >/dev/null 2>&1; then
  codex mcp remove last30days
fi
codex mcp add last30days \
  --env "LAST30DAYS_SERVICE_SOCKET=${SOCKET_PATH}" \
  -- "${DESTINATION}"

codex mcp get last30days
