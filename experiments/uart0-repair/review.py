"""Prepare a stopped manual fixed-VDP review with its own mutable FAT image."""
import hashlib,json,shutil,subprocess
from pathlib import Path
from profile import prepare_profile,root,b
dest=b/'manual-fixed-review';assert not dest.exists();dest.mkdir()
image=dest/'card.img'
with image.open('xb') as f:f.truncate(32*1024*1024)
subprocess.run(['mkfs.fat','-F','16',str(image)],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['mmd','-i',str(image),'::/uart0'],check=True)
def copyin(path,name):subprocess.run(['mcopy','-o','-i',str(image),str(path),'::/'+name],check=True)
package=b/'console8-receiver-repair'
for path in package.iterdir():
    if path.suffix=='.bin' or path.name in ('readme.txt','firmware.txt'):copyin(path,'uart0/'+path.name)
for path in (root/'build/uart0-race/hardware-return-002').iterdir():
    if path.suffix in ('.dat','.log'):copyin(path,'uart0/'+path.name)
cfg=dest/'suite.cfg';cfg.write_text('board=Oryx manual repaired receiver review\nvdp_label=UART0 repaired diagnostic (emulator)\nvdp_flash=0\nphysical_receiver=0\n');copyin(cfg,'uart0/suite.cfg')
startup=dest/'autoexec.txt';startup.write_bytes(b'CD /uart0\r\nLOAD test.bin\r\nRUN\r\nECHO RXFIX REVIEW RETURN\r\n');copyin(startup,'autoexec.txt')
p=prepare_profile('fixed',image)
art=p/'last-run';art.mkdir(exist_ok=True)
for f in art.iterdir():
    if f.is_file():f.unlink()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
receipt=dict(profile=str(p),stopped=True,graphical_launch_performed=False,
    image_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),
    manual_command='cd '+str(p)+' && ./fab-agon-emulator',test='8 then6; expect emulator PENDING with both repaired cases valid and rescued=0')
(dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
