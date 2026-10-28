#include "NativeLogPolicy.h"
#include <assert.h>
#include <stdio.h>
int main(void){
 assert(pg_verbose_log_class("[cutscene] Updating cutscene time. finalTime: 12.5")==1);
 assert(pg_verbose_log_class("[scrCommandHash debug]  Insert to bucket (0x123)")==2);
 assert(pg_verbose_log_class("Warning: [cutscene] x Audio time isn't progressing")==3);
 assert(pg_verbose_log_class("Error: cutscene failed")==0);
 assert(pg_verbose_log_class("Warning: [cutscene] missing asset")==0);
 assert(pg_verbose_log_class("[scrCommandHash debug] missing native hash")==0);
 assert(pg_verbose_log_class("[wasm] mem: malloc arena 3200")==0);
 assert(pg_verbose_log_class("Health: memory 3600 MB")==0);
 assert(pg_verbose_log_class("Failed to say context : DUCK")==2);
 assert(pg_verbose_log_class("[ai_task] Ped with model: A_M_M failed to say: DUCK")==2);
 assert(pg_verbose_log_class("[streaming] Request failed for '27rev.yft'")==0);
 puts("PASS: informational trace classification preserves errors, other warnings and memory/health diagnostics.");
}
