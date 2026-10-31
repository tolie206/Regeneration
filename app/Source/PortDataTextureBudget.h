#ifndef PG_PORTDATA_TEXTURE_BUDGET_H
#define PG_PORTDATA_TEXTURE_BUDGET_H
static inline int pg_port_texture_ratio(int nativeBC,int stored,int astc3,int minimum) {
 if(nativeBC)return 100;
 int value=stored>=100&&stored<=400 ? stored : (astc3?140:200);
 if(minimum>=100&&minimum<=400&&value<minimum)value=minimum;
 return value;
}
#endif
