#!/usr/bin/env bash
# SessionStart hook for tc3-libraries-kb
# Ensures the deterministic toolchain is ready before /discover, /doc-shard, /verify run.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

mkdir -p "$ROOT/_meta/.pdf-cache" "$ROOT/_meta/verify"

if ! python3 -c 'import pypdf' >/dev/null 2>&1; then
  pip install --quiet --upgrade cffi cryptography >/dev/null 2>&1 || true
  pip install --quiet pypdf >/dev/null 2>&1 || {
    echo "[session-init] pypdf install FAILED — /discover etc. will not work" >&2
    exit 0  # don't break the session; surface the issue when commands run
  }
fi

# Print summary so it shows in the SessionStart context
echo "[session-init] tc3-libraries-kb ready: pypdf $(python3 -c 'import pypdf; print(pypdf.__version__)' 2>/dev/null || echo missing), cache=$ROOT/_meta/.pdf-cache"
