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
  char line[140];snprintf(line,sizeof line,"Audio output layout: bufferEnabled=%u, channels=%u (corrected channel offset 75484).",enabled,channels);
  pg_log(line);layoutReported=true;
 }
 if(pg_downmix_memory((void *)memory->data,memory->size,mixer)){
  static bool told;if(!told){char line[100];snprintf(line,sizeof line,"Audio output: surround downmixed to stereo; center/rear retained, peak protection on.");pg_log(line);told=true;}
 }
}
