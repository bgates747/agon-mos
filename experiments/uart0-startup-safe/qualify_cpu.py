"""Build/run startup-safe actual-ROM checks on Oryx, never on a board."""
import argparse, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
from lease import assert_checkout
root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('build',type=Path);p.add_argument('--attempt',default='cpu');p.add_argument('--reject-build',type=Path);a=p.parse_args()
assert a.attempt.isalnum()
b=a.build.resolve();s={}
for line in (b/'symbols.txt').read_text().splitlines():
 v,_,k=line.split();s[k]=int(v,16)
rom=(b/'MOS.bin').read_bytes()
# The release's post-main return label is local in the ZDS map. Find its
# unique actual CALL _main instead of changing protected startup to export it.
call=bytes([0xcd])+s['_main'].to_bytes(3,'little');hits=[m.start() for m in re.finditer(re.escape(call),rom)]
assert len(hits)==1,hits
s['__warmboot_magic']=hits[0]+4
(b/'symbols-boot.txt').write_text(''.join(f'{v:x} T {k}\n' for k,v in s.items()))
out=b/a.attempt;out.mkdir(exist_ok=False)
for name,source in [('boot',root/'experiments/uart0-startup-safe/boot.rs'),('driver',root/'build/uart0-batching/runner/src/main.rs')]:
 d=out/name;(d/'src').mkdir(parents=True)
 text=source.read_text()
 if name=='driver':
  assert hashlib.sha256(source.read_bytes()).hexdigest()=='9aa4e2011e4573f4ed92611b7ab505ca72d8ef21ef43081b7c8e1c58afb1200a','Frozen UART oracle changed'
  old='u.set24(s["tx_next_ticket"],1);'
  assert old in text
  text=text.replace(old,old+'let vector=s["__2nd_jump_table"]+0x30;u.mem[vector]=0xc3;u.set24(vector+1,s["_uart0_handler"]as u32);')
  # Mirror the real interrupt-vector choice rather than always injecting tx_isr.
  text=text.replace('self.at("tx_isr")as u32','self.u.u24(self.at("__2nd_jump_table")+0x31)')
  # The unchanged stock ISR consumes one byte per IRQ, rather than the
  # experimental dispatcher's whole RX budget. Installed callbacks exclude
  # opening a session (BUSY), without running experimental ISR context hooks.
  text=text.replace('r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.irq();',
                    'r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;while !r.u.rx.is_empty(){r.irq();}')
  text=text.replace('assert_eq!(r.u.mem[record],4);','assert_eq!(r.u.mem[record],1);')
  text=text.replace('assert!(self.u.iirs.len()-ni<=8,"ISR cause budget exceeded");','assert!(self.u.iirs.len()-ni<=8,"ISR cause budget exceeded");')
  extra=(root/'experiments/uart0-startup-safe/controls.rs').read_text()
  text=text.replace('production(&image,&s);println!', 'startup_controls(&image,&s);production(&image,&s);println!')+extra
 (d/'src/main.rs').write_text(text)
 (d/'Cargo.toml').write_text('[package]\nname="startup-safe-'+name+'"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nez80={path="'+str(root/'build/uart0-async/ez80-model')+'"}\n')
 subprocess.run([str(Path.home()/'.cargo/bin/cargo'),'build','--offline','--release','--manifest-path',str(d/'Cargo.toml')],check=True,stdout=(d/'build.log').open('w'),stderr=subprocess.STDOUT)
 exe=d/'target/release'/('startup-safe-'+name)
 if name=='boot':
  assert_checkout()
  with (d/'execution.log').open('w') as f:subprocess.run([str(exe),str(b/'MOS.bin'),str(b/'symbols-boot.txt')],check=True,stdout=f,stderr=subprocess.STDOUT)
 else:
  for n in (1,2,4,8,16):
   assert_checkout()
   with (d/f'batch-{n}.log').open('w') as f:subprocess.run([str(exe),str(b/'MOS.bin'),str(b/'symbols.txt')],env=dict(os.environ,UART_BATCH_SIZE=str(n)),check=True,stdout=f,stderr=subprocess.STDOUT)
  if a.reject_build:
   old=a.reject_build.resolve()
   assert_checkout()
   control=subprocess.run([str(exe),str(old/'MOS.bin'),str(old/'symbols.txt')],env=dict(os.environ,UART_BATCH_SIZE='16'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
   (d/'negative-rst18.log').write_text(control.stdout)
   assert control.returncode!=0 and 'no entry found for key' not in control.stdout,'Bad RST18 image was not rejected for a runtime reason'
receipt=dict(passed=True,ROM_sha256=hashlib.sha256(rom).hexdigest(),ZDS_II=True,actual_linked_instructions=True,physical_qualification=False,rejected_previous_RST18_image=str(a.reject_build) if a.reject_build else None,
 harness_sources={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__),root/'experiments/uart0-startup-safe/boot.rs',root/'experiments/uart0-startup-safe/controls.rs',root/'build/uart0-batching/runner/src/main.rs')})
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
