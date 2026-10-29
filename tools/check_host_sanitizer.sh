#!/bin/bash
# Host-only compiler/runtime compatibility check. Never used to compile the iPhone app.
set -euo pipefail
scratch="${1:?temporary folder required}"
cc="${PG_HOST_SAN_CC:?host sanitizer compiler required}"
"$cc" --version
cat > "$scratch/host-sanitizer-probe.c" <<'C'
#include <pthread.h>
#include <setjmp.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
static jmp_buf context;
static void *thread(void *p){return p;}
int main(int argc,char **argv){
 if(argc>1&&!strcmp(argv[1],"address")){volatile char *p=malloc(8);p[16]=7;free((void*)p);return 0;}
 if(argc>1&&!strcmp(argv[1],"undefined")){volatile int x=INT_MAX;x+=1;return 0;}
 if(!setjmp(context))longjmp(context,1);
 pthread_t t;if(pthread_create(&t,0,thread,0))return 2;if(pthread_join(t,0))return 3;
 return 0;
}
C
"$cc" -g -pthread -fsanitize=address,undefined -fno-sanitize-recover=all "$scratch/host-sanitizer-probe.c" -o "$scratch/host-sanitizer-probe"
"$scratch/host-sanitizer-probe"
if "$scratch/host-sanitizer-probe" address > "$scratch/asan-negative.log" 2>&1; then
 echo 'ERROR: ASan did not reject a known heap overflow';exit 1
fi
grep -q 'AddressSanitizer: heap-buffer-overflow' "$scratch/asan-negative.log"
if "$scratch/host-sanitizer-probe" undefined > "$scratch/ubsan-negative.log" 2>&1; then
 echo 'ERROR: UBSan did not reject signed overflow';exit 1
fi
grep -q 'runtime error: signed integer overflow' "$scratch/ubsan-negative.log"
echo 'PASS: host sanitizer startup, pthread/setjmp and both intentional-error detection controls'
