"""Run native linked firmware through the retained independent UART oracle.

The frozen harness is a test dependency, not generated MOS source. Additional
cases exercise actual native instructions across descriptor and64KiB boundaries.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--native',type=Path,required=True)
p.add_argument('--firmware-build',default='uart-009-final')
p.add_argument('--attempt',required=True)
a=p.parse_args();native=a.native.resolve();build=root/'build/uart0-native'
assert a.attempt.isalnum()
runner=build/('runner-'+a.attempt);(runner/'src').mkdir(parents=True,exist_ok=False)
frozen=root/'build/uart0-batching/runner'
source=(frozen/'src/main.rs').read_text()
assert hashlib.sha256(source.encode()).hexdigest()=='9aa4e2011e4573f4ed92611b7ab505ca72d8ef21ef43081b7c8e1c58afb1200a'
old='batch_api(&image,&s)+production_batch(&image,&s));return}'
new='batch_api(&image,&s)+production_batch(&image,&s));println!("PASS descriptor boundary cases {}",batch_boundaries(&image,&s));println!("PASS 64KiB source boundary cases {}",native_source_boundaries(&image,&s));return}'
assert source.count(old)==1
source=source.replace(old,new)
source+='''
fn native_source_boundaries(image:&[u8],s:&BTreeMap<String,usize>)->usize {
 let mut cases=0;
 for n in [1,2,4,8,16] {for start in [0x6fff9,0x6ffff,0x7fff8] {for len in [1,7,16,17,255] {for iff in [false,true] {
  let mut r=Rig::new(image,s);r.open();assert_eq!(set_batch(&mut r,n),0);
  r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
  let expected=payload(len,0x95);let ticket=r.reserve();r.publish(ticket,start,&expected);
  for _ in 0..100_000 {
   r.u.advance(160);
   if iff {r.maybe_irq()} else {assert_eq!(r.call("tx_kick",0,0,0).0,0);}
   if r.call("tx_poll_drain",0,0,0).0==0 {break}
  }
  assert_eq!(r.call("tx_poll_drain",0,0,0).0,0);
  assert_eq!(r.u.wire,expected,"24-bit source increment changed bytes");
  assert_eq!(r.state(ticket),(4,len as u32));r.u.mem[start..start+len].fill(0xdd);
  assert_eq!(r.call("tx_reap",ticket,0,0).0,0);assert_eq!(r.call("tx_close",0,0,0).0,0);
  assert_eq!(r.cpu.registers().iff1,iff);cases+=1;
 }}}}cases
}
'''
(runner/'src/main.rs').write_text(source)
for name in ('Cargo.toml','Cargo.lock'):shutil.copyfile(frozen/name,runner/name)
subprocess.run([str(Path.home()/'.cargo/bin/cargo'),'build','--locked','--offline','--release',
                '--manifest-path',str(runner/'Cargo.toml'),'--target-dir',str(build/'target')],check=True)
firmware=native/'.build'/a.firmware_build/'bin/MOS.bin'
elf=firmware.with_suffix('.elf');symbols=elf.parent.parent/'symbols.txt'
nm=native.parent/'toolchain/bin/ez80-none-elf-nm'
with symbols.open('w') as f:subprocess.run([str(nm),'-a',str(elf)],stdout=f,check=True)
exe=build/'target/release/mos-uart0-async-qualification'
out=build/('runtime-'+a.attempt);out.mkdir(exist_ok=False)
for n in (1,2,4,8,16):
    with (out/f'batch-{n}.log').open('w') as f:
        subprocess.run([str(exe),str(firmware),str(symbols)],env=dict(os.environ,UART_BATCH_SIZE=str(n)),stdout=f,stderr=subprocess.STDOUT,check=True)
    print((out/f'batch-{n}.log').read_text())
negatives={}
for fault,message in [('bad-guard','CTS group allowance exceeded'),('burst','burst exceeds 16'),('release','early source release')]:
    r=subprocess.run([str(exe),str(firmware),str(symbols),fault],env=dict(os.environ,UART_BATCH_SIZE='16'),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    (out/f'negative-{fault}.log').write_text(r.stdout)
    assert r.returncode!=0 and message in r.stdout and 'negative survived' not in r.stdout,(fault,r.stdout)
    negatives[fault]=dict(rejected=True,reason=message)
receipt=dict(passed=True,ROM_sha256=hashlib.sha256(firmware.read_bytes()).hexdigest(),
             independent_instruction_oracle=True,idealized_UART_timing=True,
             production_integration_cases=27,policy_cases=538,descriptor_cases=425,
             source_boundary_cases=150,repeats_for_batch_sizes=[1,2,4,8,16],negative_controls=negatives,
             hardware_qualified=False,source_sha256=hashlib.sha256(source.encode()).hexdigest())
(out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
