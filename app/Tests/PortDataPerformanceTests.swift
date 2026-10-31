import Foundation
@main struct Tests {
 static func main() {
  let input=["-textureQuality=2","-shadowQuality=0","-lodScale=0.6","-cityDensity=0.4","-shaderQuality=1","-MaxLODScale=0.2","-frameLimit=1"]
  assert(PortDataPerformance.options(input,mode:.original)==input)
  let a=PortDataPerformance.options(input,mode:.balanced)
  assert(a.contains("-textureQuality=0") && a.contains("-shadowQuality=-1") && a.contains("-lodScale=0.15"))
  assert(a.contains("-shaderQuality=1") && a.contains("-MaxLODScale=0.2") && a.contains("-frameLimit=1"))
  assert(PortDataPerformance.options(["-lodScale=0","-shadowQuality=-1"],mode:.balanced)==["-lodScale=0","-shadowQuality=-1"])
  assert(PortDataPerformance.height(900,mode:.balanced)==720 && PortDataPerformance.height(432,mode:.balanced)==432)
  assert(PortDataPerformance.height(900,mode:.maximum)==540 && PortDataPerformance.height(900,mode:.original)==900)
  print("PASS workload profile: reversible, preserves lower choices, shader safety, frame cap and extended streaming settings")
 }
}
