import Foundation
@main struct MissionControlsTest {
 static func main() {
  let sizes:[CGSize]=[CGSize(width:540,height:299),CGSize(width:568,height:320),CGSize(width:704,height:354),CGSize(width:736,height:354),CGSize(width:844,height:369),CGSize(width:932,height:409),CGSize(width:1024,height:748),CGSize(width:1366,height:1004)]
  for size in sizes {
   let safe=CGRect(origin:CGPoint(x:44,y:10),size:size)
   for utility in [false,true] {
    let frames=ManualPadLayout.frames(in:safe,utilityOnly:utility)
    assert(frames.count == (utility ? 2 : 22))
    for (name,a) in frames {
     assert(safe.contains(a),"Outside safe area: \(name), \(size)")
     for (other,b) in frames where name<other {
      assert(!a.insetBy(dx:-4,dy:-4).intersects(b.insetBy(dx:-4,dy:-4)),"Overlapping hit areas: \(name)/\(other), \(size)")
     }
    }
    if utility {assert(Set(frames.keys)==Set(["settings","mods"]))}
   }
  }
  for available in [false,true] {for stopped in [false,true] {assert(ManualPadLayout.overlayVisible(available:available,stopped:stopped)==(available && !stopped))}}
  for external in [false,true] {for hide in [false,true] {for preview in [false,true] {assert(ManualPadLayout.utilityOnly(external:external,hide:hide,preview:preview)==(external && hide && !preview))}}}
  print("PASS production manual-pad layout: 8 device sizes, no overlapping controls/hit areas, safe-area bounds; external-controller utility buttons retained")
 }
}
