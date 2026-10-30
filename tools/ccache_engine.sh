#!/bin/bash
set -euo pipefail
real="${PG_REAL_CLANG:?original Apple compiler required}"
for arg in "$@"; do
 case "$arg" in *Generated/game*.c) exec env CCACHE_DEPEND=1 CCACHE_SLOPPINESS=modules ccache "$real" "$@";; esac
done
exec "$real" "$@"
