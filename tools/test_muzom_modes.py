from pathlib import Path
import subprocess,sys
r=Path(__file__).resolve().parents[1];s=(r/'app/App/GameSettings.swift').read_text(encoding='utf8');a=s.index('enum GameMode:');b=s.index('/// Player preferences',a)
p=Path(sys.argv[1]);p.write_text('import Foundation\nenum AppLanguage { static func choose(_ s:String)->String{s} }\n'+s[a:b]+"""
assert(GameMode.allCases.count==3)
assert(GameMode.story.engineStartMode==1)
assert(GameMode.sandbox.engineStartMode==2)
assert(GameMode.zombie.rawValue==4 && GameMode.zombie.engineStartMode==2)
assert(GameMode(rawValue:3)==nil)
assert(GameMode.zombie.title=="Zombie" && !GameMode.zombie.symbol.isEmpty)
print("PASS production game modes: Story1/Sandbox2/Zombie4->Sandbox2; GTA VI3 remains distinct")
""")
subprocess.run(['swift',str(p)],check=True)
