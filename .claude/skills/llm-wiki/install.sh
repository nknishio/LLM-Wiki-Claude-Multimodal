#!/usr/bin/env bash
# llm-wiki installer (macOS / Linux).
# Installs uv if missing, then installs the `llm-wiki` CLI as an isolated
# uv tool. No system binaries (no markitdown / poppler / pandoc) -- every
# dependency is a pure-Python wheel, so this is identical across machines.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v uv >/dev/null 2>&1; then
  echo "==> installing uv"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # uv lands in ~/.local/bin or ~/.cargo/bin; make it visible for this run
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
fi

echo "==> installing llm-wiki CLI from $SKILL_DIR"
uv tool install --force "$SKILL_DIR"

echo "==> verifying"
llm-wiki doctor
echo
echo "Done. 'llm-wiki' is on your PATH (via uv tool). Try: llm-wiki --version"
