from pathlib import Path
import re,sys
root=Path(__file__).resolve().parents[1]
s=(root/'app/Source/NativeAssets.m').read_text()
a=s.index('typedef struct { PGModPiece info;');b=s.index('static uint64_t align512',a)
h=(root/'app/Source/HostInternal.h').read_text();piece=re.search(r'typedef struct \{[^\n]+\} PGModPiece;',h).group(0)
test=r"""
int main(void){
 modArchiveCount=2;modArchives=calloc(2,sizeof *modArchives);
 for(int j=0;j<2;j++){
  PGModArchive *a=&modArchives[j];a->count=j?1:608;
  snprintf(a->path,sizeof a->path,"x64/data/lang/%s.rpf",j?"american":"american_REL");
  a->slots=calloc((size_t)a->count,sizeof *a->slots);a->pieces=calloc((size_t)a->count,sizeof *a->pieces);
  for(int i=0;i<a->count;i++){
   snprintf(a->slots[i].inner,sizeof a->slots[i].inner,"label_%d.gxt2",i);
   if(i==607)strcpy(a->slots[i].inner,"global.gxt2");
   a->slots[i].info.inner=a->slots[i].inner;a->slots[i].info.offset=512ull*(i+1);a->pieces[i]=a->slots[i].info;
  }
 }
 const PGModPiece *pieces=NULL,*second=NULL;
 assert(pg_mods_for_archive("platform:\\data\\lang\\american_REL.rpf",&pieces)==608);
 assert(!strcmp(pieces[607].inner,"global.gxt2")&&pieces[607].offset==608ull*512);
 const PGModPiece *saved=pieces;
 assert(pg_mods_for_archive("/game/x64/data/lang/american.rpf",&second)==1);
 assert(saved!=second && !strcmp(saved[607].inner,"global.gxt2"));
 assert(pg_mods_for_archive("X64/DATA/LANG/AMERICAN_REL.RPF",&pieces)==608);
 assert(pieces==saved);assert(pg_mods_for_archive("unknown.rpf",&second)==0);
 for(int j=0;j<2;j++){free(modArchives[j].slots);free(modArchives[j].pieces);}free(modArchives);
 puts("PASS: all 608 language overlay entries including global beyond 256; stable pointers across archive lookups; path aliases and case.");
}
"""
# Raw C string uses single path separators, just like the engine.
# C string backslashes remain escaped.
Path(sys.argv[1]).write_text('#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <strings.h>\n#include <limits.h>\n#include <assert.h>\n'+piece+'\n'+s[a:b]+test)
