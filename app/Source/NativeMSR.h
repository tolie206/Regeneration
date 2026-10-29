#pragma once
#include <stdint.h>
static inline uint64_t pg_msr_configuration(int mode,uint32_t w,uint32_t h){
 if(mode<1||mode>3||w<320||h<180||w>8192||h>8192||(w&1)||(h&1))return 0;
 return ((uint64_t)mode<<32)|((uint64_t)w<<16)|h;
}
static inline uint32_t pg_msr_mode(uint64_t c){return (uint32_t)(c>>32);}
static inline uint32_t pg_msr_width(uint64_t c){return (uint32_t)(c>>16)&65535;}
static inline uint32_t pg_msr_height(uint64_t c){return (uint32_t)c&65535;}
