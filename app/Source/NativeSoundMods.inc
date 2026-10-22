// Startup-mounted audio, bound once per vehicle/selection on the script thread.
// No per-frame reinitialisation, guest heap allocation, renderer or mixer changes.
u64 PG_FN_AUDIO_PROFILE(w2c_game*,u64,u32,u32);
void PG_FN_FORCE_AUDIO(w2c_game*,u32,u64);
u32 PG_FN_GET_ENTITY_MODEL(w2c_game*,u32);
typedef struct {uint32_t model;char profile[64];} PGSoundChoice;
static PGSoundChoice soundChoices[128];static unsigned soundCount,soundRevision;
static pthread_mutex_t soundLock=PTHREAD_MUTEX_INITIALIZER;
static _Atomic uint32_t soundCurrentModel;
static _Atomic bool soundMonitor;
void PGEnableSoundMods(bool enabled){atomic_store(&soundMonitor,enabled);}
uint32_t PGCurrentSoundVehicle(void){return atomic_load(&soundCurrentModel);}
bool PGSelectVehicleSound(uint32_t model,const char *profile){
 if(!model||!profile||strlen(profile)>63)return false;
 for(const char *p=profile;*p;p++)if(!((*p>='a'&&*p<='z')||(*p>='0'&&*p<='9')||*p=='_'))return false;
 pthread_mutex_lock(&soundLock);unsigned i=0;while(i<soundCount&&soundChoices[i].model!=model)i++;
 if(i==soundCount&&soundCount==128){pthread_mutex_unlock(&soundLock);return false;}
 if(i==soundCount)soundCount++;
 soundChoices[i].model=model;snprintf(soundChoices[i].profile,64,"%s",profile);soundRevision++;
 pthread_mutex_unlock(&soundLock);return true;
}
static void pg_sound_mod_tick(w2c_game *instance){
 if(!atomic_load(&soundMonitor)||PGPauseMenuActive()||PGGameStatus()!=0||PGLoadSceneSeconds()!=0)return;
 static double next;double now=timeMS(CLOCK_MONOTONIC);if(now<next)return;next=now+500;
 u64 previous=pg_asi_enter_script(instance);
 u32 ped=PG_FN_PLAYER_PED_ID(instance),vehicle=ped?PG_FN_PED_VEHICLE(instance,ped,0):0;
 u32 model=vehicle?PG_FN_GET_ENTITY_MODEL(instance,vehicle):0;atomic_store(&soundCurrentModel,model);
 static u32 lastVehicle,lastModel;static unsigned lastRevision;unsigned revision;char profile[64]={0};
 pthread_mutex_lock(&soundLock);revision=soundRevision;
 for(unsigned i=0;i<soundCount;i++)if(soundChoices[i].model==model){snprintf(profile,sizeof profile,"%s",soundChoices[i].profile);break;}
 pthread_mutex_unlock(&soundLock);
 if(vehicle&&profile[0]&&(vehicle!=lastVehicle||model!=lastModel||revision!=lastRevision)){
  // Mark attempted even if absent, to avoid log/lookup floods. Selecting again retries.
  lastVehicle=vehicle;lastModel=model;lastRevision=revision;
  if(PG_FN_AUDIO_PROFILE(instance,15584440,pg_joaat(profile),3)){
   u64 stack=instance->w2c_g0;instance->w2c_g0-=64;
   snprintf(pg_pointer(&env,instance->w2c_g0,64),64,"%s",profile);
   PG_FN_FORCE_AUDIO(instance,vehicle,instance->w2c_g0);instance->w2c_g0=stack;
   char line[128];snprintf(line,sizeof line,"Sound mod: model %08x uses %s.",model,profile);pg_log(line);
  }else pg_log("Sound mod: profile not mounted; restart the app after importing/enabling the sound pack. Original sound kept.");
 }else if(!vehicle){lastVehicle=lastModel=0;}
 pg_asi_leave_script(instance,previous);
}
