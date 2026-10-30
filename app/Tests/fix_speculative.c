#include "NativeAssetHints.h"
#include <assert.h>
int main(void){PGAssetHintQueue normal={0},low={0};PGAssetHint h={0},n={.id=1,.length=64},s={.id=2,.length=64,.speculative=true};pg_asset_hint_push(&normal,n);pg_asset_hint_push(&low,s);
assert(pg_asset_hint_next(&normal,&low,0,0,16,0,&h)&&h.id==1);assert(!pg_asset_hint_next(&normal,&low,0,0,16,0,&h));assert(low.count==1);assert(pg_asset_hint_next(&normal,&low,0,0,16,4,&h)&&h.id==2);}
