#include <assert.h>
#include <stdio.h>
#include "../Source/MuZomSurvival.h"
int main(void){
 MZSurvival s=mz_new_survival();assert(mz_valid_survival(s)&&mz_night(s)&&s.weapons==0&&s.ammo==24);
 s.cash=1000;MZSurvival copy=s;assert(!mz_buy(&s,14,false)&&s.cash==copy.cash);assert(mz_buy(&s,14,true)&&s.cash==820&&s.weapons==1);assert(!mz_buy(&s,14,true));
 s.cash=0;assert(!mz_buy(&s,10,true));s.cash=1000;s.food=99;assert(!mz_buy(&s,10,true));s.ammo=9999;assert(!mz_buy(&s,13,true));
 s.cash=999999;mz_loot_reward(&s,3);assert(s.cash==1000000);s.cycle=899.5f;mz_survival_time(&s,.5);assert(!mz_night(s));s.cycle=1199.5f;mz_survival_time(&s,.5);assert(mz_night(s));
 s.hunger=0;s.thirst=0;for(int i=0;i<10000;i++)mz_survival_time(&s,1);assert(s.hunger==0&&s.thirst==0&&mz_valid_survival(s));
 copy=s;mz_survival_time(&s,NAN);assert(s.cycle==copy.cycle);s.hunger=NAN;assert(!mz_valid_survival(s));s=mz_new_survival();s.stage=99;assert(!mz_valid_survival(s));
 puts("PASS production survival: day/night, inventory, price/proximity, bounds, invalid saves, hunger/thirst");
}
