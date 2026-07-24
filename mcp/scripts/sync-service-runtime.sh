#!/usr/bin/env bash
# Stage the canonical Agent Skill runtime inside the source-checkout-independent
# MCPB. Source of truth remains skills/last30days/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="$(cd "${MCP_DIR}/.." && pwd)"
RUNTIME_SRC="${REPO_ROOT}/skills/last30days"
RUNTIME_DST="${MCP_DIR}/runtime/last30days"

if [ ! -f "${RUNTIME_SRC}/scripts/service.py" ]; then
  echo "sync-service-runtime: canonical service.py not found" >&2
  exit 1
fi

mkdir -p "${MCP_DIR}/runtime"
find "${MCP_DIR}/runtime" -mindepth 1 -delete
cp -R "${RUNTIME_SRC}" "${RUNTIME_DST}"
find "${RUNTIME_DST}" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "${RUNTIME_DST}" -type f -name "*.pyc" -delete

echo "sync-service-runtime: staged ${RUNTIME_DST}"
