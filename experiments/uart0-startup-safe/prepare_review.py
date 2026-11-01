"""Prepare a stopped menu-first Flexe review; never flash or auto-enable UART."""
import argparse,hashlib,importlib.util,json,shutil,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--name',default='uart0-startup-safe-review');a=p.parse_args()
assert all(c.isalnum() or c=='-' for c in a.name)
b=a.build.resolve();qualified=b/'flexe-jit-final';result=json.loads((qualified/'receipt.json').read_text());assert result['passed']
assert hashlib.sha256((b/'flash.bin').read_bytes()).hexdigest()=='480b476703b798cf8d93294cac42d77cad93f7747003b061520b86685c75eb57'
source=Path(result['profile']);profile=root/'.emulator'/a.name;assert not profile.exists()
assert not (source/'sdcard.img').exists(),'Qualification profile is still running'
shutil.copytree(source,profile,symlinks=True,ignore=shutil.ignore_patterns('last-run','.runtime.sha256'))
out=b/a.name;out.mkdir();card=out/'card.img'
with card.open('xb') as f:f.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(card)],check=True,stdout=subprocess.DEVNULL);subprocess.run(['mmd','-i',str(card),'::/uart0'],check=True)
def put(src,name):subprocess.run(['mcopy','-i',str(card),str(src),'::/'+name],check=True)
for name in ('test.bin','stress.bin','app.bin','checks.bin'):put(b/'fixture'/name,'uart0/'+name)
# The firmware utility is supplied for a usage-only recovery-path check.
put(b/'flash.bin','uart0/flash.bin')
startup=out/'autoexec.txt';startup.write_bytes(b'CD /uart0\r\nLOAD test.bin\r\nRUN .\r\n');put(startup,'autoexec.txt')
readme=out/'readme.txt';readme.write_text('UART0 startup-safe ZDS II MOS review.\r\n'
 'The menu opens without activating experimental transport.\r\n'
 '1 checks stock transport/discovery; 2 activates and closes twice.\r\n'
 '3 checks OTIRX with four pause cases; 4 checks masked-IFF/exit cleanup.\r\n'
 '0 runs all. Allow up to two minutes; report the last progress line on a stall.\r\n'
 'Expect UART0 STARTUP-SAFE SUITE PASS and fresh numbered Rnnnn.log files.\r\n'
 'Q returns to MOS; check DIR and ordinary keyboard input.\r\n'
 'Close/reopen the emulator to check a fresh stock boot and menu.\r\n'
 'This profile uses the compiled RX-repaired VDP for software qualification.\r\n'
 'No physical firmware is installed or approved by this review.\r\n');put(readme,'uart0/readme.txt')
(profile/'sdcard.img').symlink_to(card)
spec=importlib.util.spec_from_file_location('factory',root/'build/uart0-branding/canonical_setup.py');factory=importlib.util.module_from_spec(spec);spec.loader.exec_module(factory);factory.name_flexe_profile(profile)
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names=['flexe-agon-emulator','flexe-agon-emulator.bin','flexe-vdp.so','mos_platform.bin','mos_platform.map','esp32-firmware.bin','esp32-firmware.elf'];(profile/'.runtime.sha256').write_text(''.join(h(profile/n)+'  '+n+'\n' for n in names))
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
subprocess.run(['bash','-n','flexe-agon-emulator'],cwd=profile,check=True)
receipt=dict(prepared=True,stopped=True,profile=str(profile),card=str(card),MOS_sha256=h(profile/'mos_platform.bin'),menu_sha256=h(b/'fixture/test.bin'),startup_sha256=h(startup),automatic_transport_activation=False,hardware_qualified=False,human_review_passed=False)
(out/'prepared.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
