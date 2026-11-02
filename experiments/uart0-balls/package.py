"""Stage a self-contained appliance in the workspace; never writes an SD card."""
import hashlib,json,shutil,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=(root/sys.argv[1]).resolve();out=b/'appliance';out.mkdir(exist_ok=False)
base=root/'build/uart0-completion/run005/appliance'
for name in ('mos-stock.bin','vdp-2.16.0.bin','flash.bin','CREDITS.txt','RX-FIX-CREDITS.txt','DIAGNOSTIC-VDP-LICENSE.txt','ESP-IDF-LICENSE','FLASH-LICENSE.txt','MOS-LICENSE.txt','VDP-LICENSE.txt'):
 shutil.copyfile(base/name,out/name)
shutil.copyfile(b/'MOS.bin',out/'mos-candidate.bin');shutil.copyfile(b/'MOS.map',out/'mos-candidate.map')
shutil.copyfile(base/'vdp-test.bin',out/'vdp-test.bin');shutil.copyfile(b/'fixture/bin/balls.bin',out/'test.bin')
readme='''UART0 BOUNCING BALLS - EXPERIMENTAL DEMO
Build {build}. Intended active directory: /test/mos-uart0/balls.
Prepared in workspace; no SD deployment or hardware run has occurred.

If required, use the installed standard flash MOSlet with normal checks:
flash mos mos-candidate.bin
Expect FILE CRC6E17923C, verification OK, normal reboot.
MOS: Arthur - UART0 write-mode EXPERIMENTAL.
flash vdp vdp-test.bin
VDP subtitle: UART0 CTS diagnostic RX sync fixed.
Return to the appliance directory after each reboot.
Stock restoration files are supplied. Flashing is the operator's action.

LOAD test.bin
RUN .
Live demo runs continuously until Q. No automatic scenario endings.
1 standard, 2 async events, 3 async callback.
B changes bitmap upload / VDP circles. C toggles ball collisions.
- removes four balls; = adds four; existing balls keep moving.
R explicitly restarts the scene with the selected options.
Changing transport/output/collisions preserves the moving scene.
Rates use a rolling eight-frame window; they do not reset periodically.
Same local physics/drawing/checksum work in both output strategies.
No eZ80 VBLANK wait. Shown FPS counts ordered post-flip replies.
Stage equivalent FPS figures overlap and must not be added.
Drain is a separate first-frame observation, excluded from the FPS window.
Short taps are recovered from key state and last-event data; multiple very
rapid batched keys can still coalesce. Interrupt-side latching is follow-up.

For repeatable automated comparisons, LOAD test.bin then:
RUN . quick
12 cases, 16 balls, four frames/case. Allow about two minutes on hardware.
RUN . sweep
24 cases, 16/64 balls, eight frames/case. Allow about five minutes.
These are provisional hardware expectations, not measured completion times.
Case/frame progress is displayed. A stationary case beyond those limits
is a problem; report it rather than counting a stall as success.
Expect BALLS DEMO COMPLETE, then a working DIR command.

Logs save when you change a scenario or quit, never on a frame limit.
The latest128raw frames per scenario are retained in bounded RAM.
Summaries record total frames and the number of overwritten old records.
Each invocation reserves Rnnnn.log, updates next.txt and appends runs.log.
The clock is not used for naming. Keep these files for return/analysis.
This package does not include old reports or reset the existing counter.
Firmware transport is opt-in; ordinary startup/RST18 remain standard.
'''
identity=json.loads((b/'identity.json').read_text());(out/'readme.txt').write_bytes(readme.format(**identity).replace('\n','\r\n').encode())
(out/'DEMO-LICENSE.txt').write_text((root/'experiments/uart0-balls/LICENSE').read_text())
manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.iterdir()) if p.is_file()}
assert manifest['mos-candidate.bin']==identity['MOS_sha256']
assert manifest['vdp-test.bin']=='201ad8ab4af807c261cb92634286b2fbaedcf3879f140e820b60ab54cf707e2a'
(out/'SHA256SUMS').write_text(''.join(f'{sha}  {name}\n' for name,sha in manifest.items()))
(b/'appliance.json').write_text(json.dumps(dict(build=identity['build'],files=manifest,SD_deployed=False,physical_qualified=False),indent=2)+'\n')
print(out)
