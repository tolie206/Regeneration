#include "../Source/NativeAudioDownmix.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
int main(void){
 float guarded[8*256+2]={0};float *p=guarded+1;guarded[0]=123;guarded[8*256+1]=456;
 for(unsigned ch=0;ch<8;ch++){
  memset(p,0,8*256*sizeof(float));p[ch*256+10]=.25f;assert(pg_downmix_planar_stereo(p,8,256));
  assert(p[10]!=0||p[256+10]!=0);if(ch==0)assert(p[10]==.25f&&p[266]==0);if(ch==1)assert(p[10]==0&&p[266]==.25f);
 }
 for(unsigned i=0;i<8*256;i++)p[i]=1;pg_downmix_planar_stereo(p,8,256);for(unsigned i=0;i<512;i++)assert(isfinite(p[i])&&fabsf(p[i])<=1.000001f);
 assert(guarded[0]==123&&guarded[8*256+1]==456);
 float stereo[2]={.5f,-.4f};assert(!pg_downmix_planar_stereo(stereo,2,1));assert(stereo[0]==.5f&&stereo[1]==-.4f);
 memset(p,0,8*256*sizeof(float));p[512]=NAN;pg_downmix_planar_stereo(p,6,256);assert(isfinite(p[0]));
 unsigned char *m=calloc(1,90000);unsigned channels=6;uint64_t output=80000;
 memcpy(m+75420,&channels,4);memcpy(m+75424,&output,8);float *pcm=(float *)(void *)(m+output);pcm[512]=.25f;
 assert(pg_downmix_memory(m,90000,0)&&pcm[0]>0&&pcm[256]>0);
 assert(!pg_downmix_memory(m,85000,0));assert(!pg_downmix_memory(m,90000,UINT64_MAX));
 output=89999;memcpy(m+75424,&output,8);assert(!pg_downmix_memory(m,90000,0));free(m);
 puts("PASS every channel reaches stereo, front level preserved, peak bounded, stereo unchanged, guards intact");
}
