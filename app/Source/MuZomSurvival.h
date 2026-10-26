#pragma once
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
// POD bridge and validated save schema. All mutations belong to the main-script tick.
typedef struct {float hunger,thirst,cycle;uint32_t cash,food,water,medkits,stage,kills,weapons,ammo,shotAmmo,smgAmmo;} MZSurvival;
typedef struct {int32_t ready,hunger,thirst,cash,food,water,medkits,stage,kills,night,minutes,shop,loot,notice;} PGZombieHUD;
bool PGZombieRead(PGZombieHUD *out);
bool PGZombieAction(int32_t action);
bool PGZombieLoad(MZSurvival *out);
void PGZombieSave(MZSurvival state);
void PGZombieGroan(float volume,float pan);
static inline MZSurvival mz_new_survival(void){return (MZSurvival){.hunger=100,.thirst=100,.cycle=225,.food=1,.water=1,.ammo=24};}
static inline bool mz_valid_survival(MZSurvival s){return isfinite(s.hunger)&&isfinite(s.thirst)&&isfinite(s.cycle)&&s.hunger>=0&&s.hunger<=100&&s.thirst>=0&&s.thirst<=100&&s.cycle>=0&&s.cycle<1200&&s.cash<=1000000&&s.food<=99&&s.water<=99&&s.medkits<=99&&s.stage<=4&&s.kills<=1000000&&s.weapons<=3&&s.ammo<=9999&&s.shotAmmo<=9999&&s.smgAmmo<=9999;}
static inline bool mz_night(MZSurvival s){return s.cycle<900;}
static inline void mz_survival_time(MZSurvival *s,float dt){if(!isfinite(dt)||dt<=0)return;if(dt>1)dt=1;s->cycle=fmodf(s->cycle+dt,1200);s->hunger=fmaxf(0,s->hunger-dt/18);s->thirst=fmaxf(0,s->thirst-dt/12);}
// Buy actions: 10 food,11 water,12 first aid,13 pistol ammo,14 shotgun,15 SMG.
// No caller can bypass shop proximity or bounded arithmetic.
static inline bool mz_buy(MZSurvival *s,int action,bool near){
 if(!near||action<10||action>17)return false;
 static const unsigned price[]={15,10,35,25,180,250,40,45};unsigned p=price[action-10];if(s->cash<p)return false;
 if((action==10&&s->food>=99)||(action==11&&s->water>=99)||(action==12&&s->medkits>=99)||(action==13&&s->ammo>9900)||(action==14&&(s->weapons&1))||(action==15&&(s->weapons&2))||(action==16&&(!(s->weapons&1)||s->shotAmmo>9900))||(action==17&&(!(s->weapons&2)||s->smgAmmo>9900)))return false;
 s->cash-=p;if(action==10)s->food++;if(action==11)s->water++;if(action==12)s->medkits++;if(action==13)s->ammo+=24;if(action==14){s->weapons|=1;s->shotAmmo=32;}if(action==15){s->weapons|=2;s->smgAmmo=90;}if(action==16)s->shotAmmo+=24;if(action==17)s->smgAmmo+=60;return true;
}
static inline void mz_loot_reward(MZSurvival *s,unsigned type){switch(type%5){case 0:if(s->food<99)s->food++;break;case 1:if(s->water<99)s->water++;break;case 2:if(s->ammo<=9987)s->ammo+=12;break;case 3:s->cash=s->cash>999980?1000000:s->cash+20;break;case 4:if(s->medkits<99)s->medkits++;break;}}
