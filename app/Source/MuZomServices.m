#import <Foundation/Foundation.h>
#import <AVFAudio/AVFAudio.h>
#include "MuZomSurvival.h"
static NSURL *mzSaveURL(void){return [[[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask].firstObject URLByAppendingPathComponent:@"MuZom-survival.json"];}
bool PGZombieLoad(MZSurvival *out){
 @autoreleasepool {NSData *d=[NSData dataWithContentsOfURL:mzSaveURL()];if(!d||d.length>4096)return false;
 NSDictionary *j=[NSJSONSerialization JSONObjectWithData:d options:0 error:nil];if(![j isKindOfClass:NSDictionary.class])return false;
 NSArray *keys=@[@"version",@"hunger",@"thirst",@"cycle",@"cash",@"food",@"water",@"medkits",@"stage",@"kills",@"weapons",@"ammo",@"shotAmmo",@"smgAmmo"];
 for(NSString *k in keys)if(![j[k] isKindOfClass:NSNumber.class])return false;if([j[@"version"] intValue]!=1)return false;
 // Reject negative/fractional/overflow integers before narrowing.
 for(NSString *k in [keys subarrayWithRange:NSMakeRange(4,10)]){double v=[j[k] doubleValue];if(!isfinite(v)||v<0||v>1000000||v!=floor(v))return false;}
 MZSurvival s={[j[@"hunger"] floatValue],[j[@"thirst"] floatValue],[j[@"cycle"] floatValue],[j[@"cash"] unsignedIntValue],[j[@"food"] unsignedIntValue],[j[@"water"] unsignedIntValue],[j[@"medkits"] unsignedIntValue],[j[@"stage"] unsignedIntValue],[j[@"kills"] unsignedIntValue],[j[@"weapons"] unsignedIntValue],[j[@"ammo"] unsignedIntValue],[j[@"shotAmmo"] unsignedIntValue],[j[@"smgAmmo"] unsignedIntValue]};if(!mz_valid_survival(s))return false;*out=s;return true;}
}
void PGZombieSave(MZSurvival s){
 if(!mz_valid_survival(s))return;
 static dispatch_queue_t q;static dispatch_once_t once;dispatch_once(&once,^{q=dispatch_queue_create("vn.gta.muzom.save",DISPATCH_QUEUE_SERIAL);});
 dispatch_async(q,^{@autoreleasepool {NSDictionary *j=@{@"version":@1,@"hunger":@(s.hunger),@"thirst":@(s.thirst),@"cycle":@(s.cycle),@"cash":@(s.cash),@"food":@(s.food),@"water":@(s.water),@"medkits":@(s.medkits),@"stage":@(s.stage),@"kills":@(s.kills),@"weapons":@(s.weapons),@"ammo":@(s.ammo),@"shotAmmo":@(s.shotAmmo),@"smgAmmo":@(s.smgAmmo)};NSData *d=[NSJSONSerialization dataWithJSONObject:j options:0 error:nil];if(d)[d writeToURL:mzSaveURL() options:NSDataWritingAtomic error:nil];}});
}
// Three preloaded voices, one event per native cooldown. Do not change the game's audio session.
static NSMutableArray<AVAudioPlayer*> *mzVoices;
void PGZombiePrepareAudio(void){
 if(mzVoices)return;mzVoices=[NSMutableArray array];NSURL *root=[[[NSFileManager defaultManager] URLsForDirectory:NSDocumentDirectory inDomains:NSUserDomainMask].firstObject URLByAppendingPathComponent:@"MuZomAudio"];
 for(unsigned i=0;i<8;i++){AVAudioPlayer *p=[[AVAudioPlayer alloc] initWithContentsOfURL:[root URLByAppendingPathComponent:[NSString stringWithFormat:@"groan%u.wav",i]] error:nil];if(p){[p prepareToPlay];[mzVoices addObject:p];}}
}
void PGZombieGroan(float volume,float pan){
 dispatch_async(dispatch_get_main_queue(),^{
  static unsigned index;PGZombiePrepareAudio();
  unsigned active=0;for(AVAudioPlayer *p in mzVoices)if(p.playing)active++;if(active>=3||!mzVoices.count)return;
  for(unsigned i=0;i<mzVoices.count;i++){AVAudioPlayer *p=mzVoices[(index++)%mzVoices.count];if(p.playing)continue;p.volume=fminf(1,fmaxf(0,volume));p.pan=fminf(1,fmaxf(-1,pan));p.currentTime=0;[p play];break;}
 });
}
