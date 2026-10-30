import UIKit
/// Changes are saved only. The renderer reads them at the next engine start.
enum RendererFixOptions {
 static func items(settings:GameSettings,changed:@escaping()->Void)->[UIMenuElement]{
  let fxaa=UIAction(title:"FXAA · mềm cạnh (có thể tăng tải GPU)",state:settings.fixFXAA ? .on:.off){_ in settings.fixFXAA.toggle();changed()}
  let event=UIAction(title:"Giảm gửi event GPU đã hoàn tất",state:settings.fixEventFast ? .on:.off){_ in settings.fixEventFast.toggle();changed()}
  let trace=UIAction(title:"Trace render giới hạn (chẩn đoán)",state:settings.fixTrace ? .on:.off){_ in settings.fixTrace.toggle();changed()}
  let speculation=UIAction(title:"Tắt đọc đoán trước (thử nghiệm)",state:settings.fixNoSpeculation ? .on:.off){_ in settings.fixNoSpeculation.toggle();changed()}
  let batch=[0.0,0.25,0.5,1.0].map{delay in UIAction(title:delay==0 ? "Gom query: tắt (gốc)":"Gom query: \(delay) ms · thử nghiệm",state:settings.fixQueryBatch==delay ? .on:.off){_ in settings.fixQueryBatch=delay;changed()}}
  return [fxaa,event,trace,speculation]+batch.map{$0 as UIMenuElement}
 }
}
