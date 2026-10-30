#!/bin/bash
set -euo pipefail
real="${PG_REAL_CLANG:?original Apple compiler required}"
for arg in "$@"; do
 case "$arg" in *Generated/game*.c) exec /usr/bin/python3 "$(dirname "$0")/ccache_engine.py" "$@";; esac
done
exec "$real" "$@"
