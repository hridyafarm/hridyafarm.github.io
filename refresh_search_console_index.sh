#!/bin/zsh
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$ROOT_DIR/generate_sitemap.py"

if [[ -n "${GSC_ACCESS_TOKEN:-}" ]]; then
  python3 "$ROOT_DIR/submit_search_console_sitemap.py"
else
  echo "Sitemap updated locally. Set GSC_ACCESS_TOKEN to submit it to Search Console automatically."
fi
