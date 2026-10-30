#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include <time.h>
#include <assert.h>
#include <stdio.h>
typedef uint64_t u64;typedef uint32_t u32;typedef struct{int unused;}w2c_game;
static unsigned char bytes[19520606];static struct{struct{unsigned char *data;unsigned size;}memory;}env={{bytes,sizeof bytes}};
static int configuredStartMode=1,status,paused;static bool loading;static double now;static unsigned calls;
static int PGPauseMenuActive(void){return paused;}static int PGGameStatus(void){return status;}static bool PGLoadSceneActive(void){return loading;}
static double timeMS(int c){(void)c;return now;}static u64 pg_asi_enter_script(w2c_game*i){(void)i;return 1;}static void pg_asi_leave_script(w2c_game*i,u64 p){(void)i;assert(p==1);}
static void pg_log(const char*s){(void)s;}
#include "../Source/NativeSandboxMap.inc"
void PG_FN_HIDE_MAP_FOW(w2c_game*i,u32 v){(void)i;assert(v==1);bytes[19520605]=1;calls++;}
int main(void){w2c_game i={0};pg_sandbox_map_tick(&i);assert(calls==0);configuredStartMode=3;pg_sandbox_map_tick(&i);assert(calls==0);configuredStartMode=2;loading=true;pg_sandbox_map_tick(&i);assert(calls==0);loading=false;pg_sandbox_map_tick(&i);assert(calls==1);now=2000;pg_sandbox_map_tick(&i);assert(calls==1);bytes[19520605]=0;now=3000;pg_sandbox_map_tick(&i);assert(calls==2);puts("PASS sandbox-only FoW, no story/test-map change, bounded reapply");}
