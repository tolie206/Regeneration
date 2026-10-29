#!/bin/bash
set -uo pipefail
scratch="${1:?temporary folder required}"
"${PG_HOST_SAN_CC:-clang}" -std=c11 -g -Wall -Wextra -Werror -pthread -fsanitize=address,undefined app/Tests/lazy_cpu.c -o "$scratch/lazy-cpu" || exit 1
"$scratch/lazy-cpu"
result=$?
if test "$result" != 0; then
  printf 'Sanitized lazy test exited %s; collecting backtrace and runtime controls.\n' "$result"
  xcrun lldb --batch -o 'settings set target.disable-aslr false' -o run -o 'thread backtrace all' -- "$scratch/lazy-cpu" || true
  cat > "$scratch/sanitizer-control.c" <<'C'
#include <setjmp.h>
static jmp_buf context;
int main(void){if(!setjmp(context))longjmp(context,1);return 0;}
C
  "${PG_HOST_SAN_CC:-clang}" -g -fsanitize=address,undefined "$scratch/sanitizer-control.c" -o "$scratch/sanitizer-control" && "$scratch/sanitizer-control"
  printf 'Minimal sanitized setjmp/longjmp control exit: %s\n' "$?"
  clang -std=c11 -g -Wall -Wextra -Werror -pthread app/Tests/lazy_cpu.c -o "$scratch/lazy-plain" && "$scratch/lazy-plain"
  printf 'Unsanitized full test control exit: %s\n' "$?"
  exit "$result"
fi
"$scratch/lazy-cpu" --disabled || exit 1
clang -std=c11 -Wall -Wextra -Werror -I app/Source app/Tests/log_policy.c -o "$scratch/log-policy" || exit 1
"$scratch/log-policy"
