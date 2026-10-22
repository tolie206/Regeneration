import unittest,zipfile,struct,json,re,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def parse(b):
 assert b[:4]==b'2TXG';n=struct.unpack_from('<I',b,4)[0]
 assert b[8+8*n:12+8*n]==b'2TXG' and struct.unpack_from('<I',b,12+8*n)[0]==len(b)
 values={}
 for i in range(n):
  h,at=struct.unpack_from('<II',b,8+8*i);assert 16+8*n<=at<len(b)
  assert h not in values;values[h]=b[at:b.index(0,at)].decode('utf8')
 return values
class Translation(unittest.TestCase):
 def test_accented_and_plain_keep_same_labels_and_control_tokens(self):
  with zipfile.ZipFile(ROOT/'app/Resources/VietnameseAccented.zip') as a,zipfile.ZipFile(ROOT/'app/Resources/VietnamesePlain.zip') as p:
   names=p.namelist();self.assertEqual(len(names),602);total=0;accented=False
   for n in names:
    x,y=parse(a.read(n)),parse(p.read(n));self.assertEqual(x.keys(),y.keys());total+=len(x)
    for key in x:
     self.assertEqual(re.findall(r'~[^~]*~',x[key]),re.findall(r'~[^~]*~',y[key]))
     plain=re.sub(r"~[^~]*~","",y[key]);self.assertFalse(any(unicodedata.combining(c) for c in unicodedata.normalize("NFD",plain)));self.assertNotIn("đ",plain);self.assertNotIn("Đ",plain);accented |= any(ord(c)>127 for c in x[key])
   self.assertTrue(accented);self.assertEqual(total,213683)
   self.assertEqual(len(a.namelist())-len(names),5)
 def test_vietnamese_format_placeholders_are_preserved(self):
  catalog=json.loads((ROOT/'app/App/Localizable.xcstrings').read_text(encoding='utf8'))
  for key,value in catalog['strings'].items():
   vi=value.get('localizations',{}).get('vi',{}).get('stringUnit',{}).get('value')
   if vi:self.assertEqual(sorted(re.findall(r'\{arg[0-9]+\}',key)),sorted(re.findall(r'\{arg[0-9]+\}',vi)),key)
if __name__=='__main__':unittest.main()
