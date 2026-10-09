#!/usr/bin/env bash
# Render the site; fail on render errors or unresolved internal links.
set -uo pipefail
dir="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
log=$(mktemp)
trap 'rm -f "$log"' EXIT
quarto render "$dir" 2>&1 | tee "$log"
status=${PIPESTATUS[0]}
if [ "$status" -ne 0 ]; then
    echo "render failed (exit $status)"
    exit "$status"
fi
if grep -q "Unable to resolve link target" "$log"; then
    echo "broken internal link(s):"
    grep "Unable to resolve link target" "$log"
    exit 1
fi
echo "render ok"
