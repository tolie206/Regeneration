#pragma once
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
// Standard planar 5.1/7.1: L,R,C,LFE,SL,SR[,BL,BR]. Stereo input untouched.
// Preserve front-only level. Normalize only blocks whose summed peak exceeds1.
static inline bool pg_downmix_planar_stereo(float *pcm,unsigned channels,unsigned frames){
 if(!pcm||!frames||(channels!=6&&channels!=8))return false;
 float peak=1;
 for(unsigned i=0;i<frames;i++){
  float v[8]={0};for(unsigned c=0;c<channels;c++){float f=pcm[c*frames+i];v[c]=isfinite(f)?f:0;}
  float l=v[0]+.70710678f*(v[2]+v[4])+.5f*v[3];
  float r=v[1]+.70710678f*(v[2]+v[5])+.5f*v[3];
  if(channels==8){l+=.5f*v[6];r+=.5f*v[7];}
  pcm[i]=l;pcm[frames+i]=r;peak=fmaxf(peak,fmaxf(fabsf(l),fabsf(r)));
 }
 if(peak>1){float gain=1/peak;for(unsigned i=0;i<frames*2;i++)pcm[i]*=gain;}
 return true;
}

static inline bool pg_downmix_memory(void *base,uint64_t size,uint64_t mixer){
 if(!base||mixer>size||size-mixer<75488)return false;
 unsigned enabled,channels;uint64_t output;unsigned char *memory=base;
 // Engine checks +75420 for nonzero buffer state, NOT channel count. MixBuffers loops +75484.
 memcpy(&enabled,memory+mixer+75420,4);
 memcpy(&channels,memory+mixer+75484,4);memcpy(&output,memory+mixer+75424,8);
 if(!enabled||(channels!=6&&channels!=8)||!output||output%4)return false;
 uint64_t bytes=(uint64_t)channels*256*4;
 if(output>size||bytes>size-output)return false;
 return pg_downmix_planar_stereo((float *)(void *)(memory+output),channels,256);
}
