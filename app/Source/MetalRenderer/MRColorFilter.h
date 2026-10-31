#pragma once
#include <stdint.h>
// 16 bytes, matches Metal constant float4 at fragment buffer1.
typedef struct {float saturation, green, contrast, strength;} PGColorParams;
static inline PGColorParams pg_color_params(uint32_t mode){
 switch(mode){
 case 1:return (PGColorParams){1.04f,1.12f,1.01f,1}; // natural
 case 2:return (PGColorParams){1,1.24f,1,1}; // green-selective; neutral/skin unchanged
 case 3:return (PGColorParams){1.10f,1.16f,1.025f,1}; // vivid
 default:return (PGColorParams){1,1,1,0};
 }
}
