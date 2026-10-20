from pathlib import Path
import json
from skoolkit.snapshot import Snapshot
from emulator import setup,run,MemoryView
ROOT=Path(__file__).resolve().parents[1]
loading=(ROOT/'assets/loading.scr').read_bytes()
raw=(ROOT/'dist/Tetris_GB.tap').read_bytes();blocks=[];pos=0
while pos<len(raw):
 size=int.from_bytes(raw[pos:pos+2],'little');pos+=2;block=raw[pos:pos+size];pos+=size
 assert len(block)==size
 parity=0
 for b in block:parity^=b
 assert parity==0
 blocks.append(block)
assert blocks[3][1:-1]==loading
assert int.from_bytes(blocks[2][14:16],'little')==16384
snap=Snapshot.get(str(ROOT/'dist/Tetris_GB.z80'))
assert bytes(snap.ram()[:6912])==loading
s,t=setup(str(ROOT/'dist/Tetris_GB.z80'));run(s,t,100)
assert bytes(MemoryView(s.memory)[16384:23296])!=loading
S=json.loads((ROOT/'symbols.json').read_text());assert s.memory[S['mode']]==0
report={'screen_bytes':len(loading),'valid_tape_checksums':True,'loading_screen_embedded_at_16384':True,'fresh_ROM_load_preserves_loading_image_until_entry':True,'menu_opens_after_loading':True}
(ROOT/'validation_loading.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
