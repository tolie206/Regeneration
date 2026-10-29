from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class MissionControls(unittest.TestCase):
 def test_manual_sticks_bypass_prompt_and_swipe(self):
  s=(ROOT/'app/App/TouchControlsView.swift').read_text(encoding='utf8')
  self.assertIn('!manualPadEnabled && GameSettings.shared.cameraTouchMode',s)
  begin=s[s.index('    private func beginTouch('):s.index('    private func press(')]
  self.assertLess(begin.index('else if manualPadEnabled'),begin.index('else if context == .menu'))
  output=s[s.index('    func padState('):s.index('    /// Swipe camera (mouse):')]
  manual=output[output.index('        if manualPadEnabled {'):output.index('        switch context {')]
  for token in ['state.rightX=Float(look.x)','state.rightY=Float(look.y)','state.leftX=Float(moveStick.value.x)','mission.trigger==1','mission.trigger==2','held.insert(.l3)','held.insert(.r3)']:self.assertIn(token,manual)
  self.assertIn('return state',manual)
 def test_manual_editor_group_and_collision_guard(self):
  editor=(ROOT/'app/App/ControlsLayout.swift').read_text(encoding='utf8')
  self.assertIn('groupPicker.selectedSegmentIndex == 3 ? "manual"',editor)
  self.assertIn('controls.setManualPadPreview(groupPicker.selectedSegmentIndex == 3)',editor)
  self.assertIn('replacing:button.name,entry:proposal',editor)
  touch=(ROOT/'app/App/TouchControlsView.swift').read_text(encoding='utf8')
  self.assertIn('manualPadEnabled ? "manual"',touch)
  self.assertIn('ControlsLayout.manualFrames(in:safe)',touch)
 def test_hardware_keeps_overlay_but_not_gameplay_touches(self):
  s=(ROOT/'app/App/NativePortViewController.swift').read_text(encoding='utf8')
  self.assertIn('touchControls.isHidden = !overlayVisible',s)
  self.assertNotIn('touchControls.isHidden = !touchActive',s)
  s=(ROOT/'app/App/TouchControlsView.swift').read_text(encoding='utf8')
  self.assertIn('if utilityOnly { return [settings, mods] }',s)
  self.assertIn('if utilityOnly {return button(at:point) == nil ? nil : self}',s)
  self.assertIn('if utilityOnly { return PGPadState() }',s)
if __name__=='__main__':unittest.main()
