import Foundation
@main struct Tests {
 static func main() throws {
  let fm=FileManager.default,root=fm.temporaryDirectory.appendingPathComponent("port-rpf-"+UUID().uuidString)
  try fm.createDirectory(at:root,withIntermediateDirectories:true);defer{try? fm.removeItem(at:root)}
  func put(_ d:inout Data,_ at:Int,_ value:UInt32) { for j in 0..<4 {d[at+j]=UInt8(truncatingIfNeeded:value >> (j*8))} }
  func make(_ key:UInt32,_ children:[(String,Data)] = []) -> Data {
   let count=children.count+1;var strings=Data([0]),offsets:[Int]=[]
   for (name,_) in children {offsets.append(strings.count);strings.append(Data(name.utf8));strings.append(0)}
   var d=Data(count:512);put(&d,0,0x52504637);put(&d,4,UInt32(count));put(&d,8,UInt32(strings.count));put(&d,12,key)
   put(&d,20,0x7fffff00);put(&d,24,1);put(&d,28,UInt32(children.count));d.replaceSubrange((16+count*16)..<(16+count*16+strings.count),with:strings)
   for (i,item) in children.enumerated() {
    let at=16+(i+1)*16;put(&d,at,UInt32(offsets[i]));put(&d,at+4,UInt32(d.count/512)<<8);put(&d,at+8,UInt32(item.1.count))
    d.append(item.1);while d.count%512 != 0 {d.append(0)}
   };return d
  }
  let a=make(0,[ ("inner.rpf",make(0)) ]),b=make(PortDataRPFNormalizer.open,[("inside.rpf",make(0))]),encrypted=make(0x0ffffff9)
  let rows:[(String,Data)]=[("a.rpf",a),("b.rpf",b),("encrypted.rpf",encrypted)]
  for (name,bytes) in rows {try bytes.write(to:root.appendingPathComponent(name))}
  let files=rows.map{($0.0,UInt64($0.1.count))}
  let changed=try PortDataRPFNormalizer.prepare(folder:root,files:files);assert(changed==3)
  for (name,before) in rows {
   let after=try Data(contentsOf:root.appendingPathComponent(name));assert(after.count==before.count)
   let allowed=Set(name=="a.rpf" ? [12,13,14,15,524,525,526,527]:name=="b.rpf" ? [524,525,526,527]:[])
   for i in before.indices where !allowed.contains(i) {assert(before[i]==after[i],"payload changed")}
  }
  let second=try PortDataRPFNormalizer.prepare(folder:root,files:files);assert(second==0)
  assert(fm.fileExists(atPath:root.appendingPathComponent("mugoat-rpf-open-repair.json").path))
  // Plan failure must precede writes even if an earlier file needs fixing.
  try a.write(to:root.appendingPathComponent("a.rpf"));var broken=make(0);put(&broken,4,100001);try broken.write(to:root.appendingPathComponent("bad.rpf"))
  do {_=try PortDataRPFNormalizer.prepare(folder:root,files:[("a.rpf",UInt64(a.count)),("bad.rpf",UInt64(broken.count))]);fatalError("accepted bad table")}catch{}
  let untouched = try Data(contentsOf:root.appendingPathComponent("a.rpf"));assert(untouched==a)
  print("PASS RPF startup repair: NONE -> OPEN, nested/OPEN-parent, encrypted unchanged, payload unchanged, idempotent, reject before writing")
 }
}
