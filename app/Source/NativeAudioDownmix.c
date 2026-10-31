// Runs on the existing mixer thread, after MixBuffers and before stereo-ring publication.
#include "HostInternal.h"
#include "NativeAudioDownmix.h"
#include <string.h>
#include <stdio.h>
static _Atomic bool downmixEnabled=true;
void PGConfigureAudioDownmix(int enabled){atomic_store(&downmixEnabled,enabled!=0);}
void pg_audio_downmix_output(w2c_game *instance,u64 mixer){
 if(!atomic_load(&downmixEnabled))return;
 wasm_rt_shared_memory_t *memory=instance->w2c_env_memory;
 static bool layoutReported;
 if(!layoutReported&&mixer<=memory->size&&memory->size-mixer>=75488){
  const unsigned char *m=(const unsigned char *)(void *)memory->data;unsigned channels,enabled;
  memcpy(&channels,m+mixer+75484,4);memcpy(&enabled,m+mixer+75420,4);
  char line[140];snprintf(line,sizeof line,"Audio output layout: bufferState=%u, channels=%u (corrected channel offset 75484).",enabled,channels);
  pg_log(line);layoutReported=true;
 }
 if(pg_downmix_memory((void *)memory->data,memory->size,mixer)){
  static bool told;if(!told){char line[100];snprintf(line,sizeof line,"Audio output: surround downmixed to stereo; center/rear retained, peak protection on.");pg_log(line);told=true;}
 }
}

extern void pg_note_granular_block(bool nonzero);
void pg_granular_output_probe(w2c_game *instance,u64 output){
 static _Thread_local unsigned blocks;if((++blocks&255)!=0)return;
 wasm_rt_shared_memory_t *m=instance->w2c_env_memory;
 if(!output||output%4||output>m->size||m->size-output<1024)return;
 const unsigned char *p=(const unsigned char *)(void *)m->data;bool nonzero=false;
 for(unsigned i=0;i<256;i++){float f;memcpy(&f,p+output+i*4,4);if(isfinite(f)&&fabsf(f)>1e-7f){nonzero=true;break;}}
 pg_note_granular_block(nonzero);
}
