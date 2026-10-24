"""Read-only RPF/GXT inspection for the owner's local compatibility fixtures."""
from pathlib import Path
import struct, zlib, json

def entries(b):
    word=lambda p: struct.unpack_from('<I',b,p)[0]
    assert word(0)==0x52504637
    n,sz,enc=word(4),word(8),word(12)
    assert enc in (0,0x4e45504f), 'encrypted RPF table'
    names=16+n*16
    def walk(i,parent=''):
        a,c,u,g=struct.unpack_from('<IIII',b,16+i*16)
        p=names+(a if c==0x7fffff00 else a&65535)
        name=b[p:b.index(0,p)].decode().lower()
        path='/'.join(x for x in (parent,name) if x)
        if c==0x7fffff00:
            for j in range(u,u+g): yield from walk(j,path)
        else:
            packed=a|(c<<32);resource=bool(c&0x80000000)
            size=(packed>>16)&0xffffff;offset=((packed>>40)&(0x7fffff if resource else 0xffffff))*512
            if not resource and not size: size=u
            assert offset+size<=len(b)
            data=b[offset:offset+size]
            if not resource and ((packed>>16)&0xffffff): data=zlib.decompress(data,-15)
            yield path,data,resource
    yield from walk(0)

def gxt(b):
    assert b[:4]==b'2TXG'
    n=struct.unpack_from('<I',b,4)[0]
    return {h:b[p:b.index(0,p)].decode('utf-8') for h,p in
            (struct.unpack_from('<II',b,8+i*8) for i in range(n))}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]/'mod-audit'
    for p in root.rglob('dlc.rpf'):
        try:
            rows=list(entries(p.read_bytes()))
            print(p.parent.name,len(rows),'entries')
            if 'sound' in str(p):
                for name,data,resource in rows:
                    if name.endswith('.dat151.rel'):
                        length=struct.unpack_from('<I',data,4)[0]
                        at=8+length;size=struct.unpack_from('<I',data,at)[0]
                        print(name,'names',repr(data[at+4:at+4+min(size,160)]))
        except (AssertionError,ValueError,zlib.error) as e: print('UNREADABLE',p.parent.name,str(e))
