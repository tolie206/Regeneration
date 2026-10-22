#include <stdint.h>
#include <zlib.h>
int gi_inflate_raw(const void *in,uint32_t n,void *out,uint32_t capacity){
 z_stream s={0};s.next_in=(Bytef*)in;s.avail_in=n;s.next_out=out;s.avail_out=capacity;
 if(inflateInit2(&s,-MAX_WBITS)!=Z_OK)return 0;
 int result=inflate(&s,Z_FINISH);int ok=result==Z_STREAM_END&&s.total_out==capacity&&s.total_in==n;inflateEnd(&s);return ok;
}
