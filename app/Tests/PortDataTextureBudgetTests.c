#include <assert.h>
#include <stdio.h>
#include "../Source/PortDataTextureBudget.h"
int main(void){
 assert(pg_port_texture_ratio(0,129,1,200)==200);
 assert(pg_port_texture_ratio(0,199,1,200)==200);
 assert(pg_port_texture_ratio(0,220,1,200)==220);
 assert(pg_port_texture_ratio(0,129,1,0)==129);
 assert(pg_port_texture_ratio(0,0,1,0)==140);
 assert(pg_port_texture_ratio(0,0,0,0)==200);
 assert(pg_port_texture_ratio(1,300,1,200)==100);
 assert(pg_port_texture_ratio(0,140,1,999)==140);
 assert((4096-1800)*100/pg_port_texture_ratio(0,129,1,200)==1148);
 puts("PASS boot budget: observed129% cannot inflate PortData budget, native BC unchanged, off restores original");return 0;
}
