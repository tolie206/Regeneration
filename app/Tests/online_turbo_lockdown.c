#define PG_ROLEPLAY_CLIENT 1
#define main offline_tests_not_executed
#include "turbo_runtime.c"
#undef main
int main(void){PGTurboConfig c=PGTurboDefaultConfig();c.enabled=true;assert(!PGSetTurboConfig(c));return 0;}
