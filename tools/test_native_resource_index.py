from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1];p=Path(sys.argv[1])
s=(root/'app/Source/NativeAssets.m').read_text();a=s.index('uint32_t pg_mods_large_resource_size(');b=s.index('\n}\n',a)+3
p.write_text(r"""
#import <Foundation/Foundation.h>
#include <stdint.h>
#include <assert.h>
static NSString *fixtureRoot;
static NSString *modsFolder(void){return fixtureRoot;}
"""+s[a:b]+r"""
int main(int argc,char **argv){@autoreleasepool{
 assert(argc==2);fixtureRoot=@(argv[1]);
 assert(pg_mods_large_resource_size("dlc_vf8:/x64/levels/gta5/vehicles/vehicles.rpf","vf8.yft",0xa01a1786,0x20000000)==17512137);
 assert(pg_mods_large_resource_size("DLC_VF8:\\X64\\LEVELS\\GTA5\\VEHICLES\\VEHICLES.RPF","VF8_HI.YFT",0xa01a1786,0x20000000)==17502433);
 assert(pg_mods_large_resource_size("dlc_vf8:/x64/levels/gta5/vehicles/vehicles.rpf","vf8.yft",0,0)==0);
 assert(pg_mods_large_resource_size("other:/vehicles.rpf","vf8.yft",0xa01a1786,0x20000000)==0);
}return 0;}
""")
subprocess.run(['clang','-fobjc-arc','-fblocks','-framework','Foundation',str(p),'-o',str(p.with_suffix(''))],check=True)
subprocess.run([str(p.with_suffix('')),sys.argv[2]],check=True)
print('PASS native JSON index lookup on actual imported VF8 metadata: case/slash aliases, exact flags, unrelated archive rejected')
