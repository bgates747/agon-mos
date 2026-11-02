"""Prepare baseline regressions, adjusting only versioned ABI expectations."""
import hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=Path(sys.argv[1]).resolve();o=b/'regression';(o/'src').mkdir(parents=True,exist_ok=False)
p=root/'build/uart0-batching/runner/src/main.rs';assert hashlib.sha256(p.read_bytes()).hexdigest()=='9aa4e2011e4573f4ed92611b7ab505ca72d8ef21ef43081b7c8e1c58afb1200a'
s=p.read_text().split('fn main(){')[0]
s=s.replace('u.set24(s["tx_next_ticket"],1);','u.set24(s["tx_next_ticket"],1);let vector=s["__2nd_jump_table"]+0x30;u.mem[vector]=0xc3;u.set24(vector+1,s["_uart0_handler"]as u32);')
s=s.replace('self.at("tx_isr")as u32','self.u.u24(self.at("__2nd_jump_table")+0x31)')
s=s.replace('r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.irq();','r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;while !r.u.rx.is_empty(){r.irq();}')
s=s.replace('assert_eq!(r.u.mem[record],4);','assert_eq!(r.u.mem[record],1);')
s=s.replace('if batching{2}else{1}', 'if s.contains_key("tx_write_config"){3}else if batching{2}else{1}')
s=s.replace('if batching{54}else{46}', 'if s.contains_key("tx_write_config"){69}else if batching{54}else{46}')
s=s.replace('assert_eq!(r.u.mem[table as usize+7],15);','assert_eq!(r.u.mem[table as usize+7],if s.contains_key("tx_write_config"){31}else{15});')
s+=(root/'experiments/uart0-startup-safe/controls.rs').read_text()
s+='''
fn main(){let a:Vec<_>=env::args().collect();let image=fs::read(&a[1]).unwrap();let s=fs::read_to_string(&a[2]).unwrap().lines().map(|l|{let p:Vec<_>=l.split_whitespace().collect();(p[2].into(),usize::from_str_radix(p[0],16).unwrap())}).collect();startup_controls(&image,&s);production(&image,&s);println!("PASS batching regression cases {}",batch_api(&image,&s)+production_batch(&image,&s));}
'''
(o/'src/main.rs').write_text(s)
(o/'Cargo.toml').write_text('[package]\nname="uart0-completion-regression"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nez80={path="'+str(root/'build/uart0-async/ez80-model')+'"}\n')
boot=b/'boot';(boot/'src').mkdir(parents=True);(boot/'src/main.rs').write_bytes((root/'experiments/uart0-startup-safe/boot.rs').read_bytes());(boot/'Cargo.toml').write_text((o/'Cargo.toml').read_text().replace('uart0-completion-regression','uart0-completion-boot'))
# Derive protected reset return label without changing upstream source.
syms={k:int(v,16) for v,_,k in (l.split() for l in (b/'symbols.txt').read_text().splitlines())};rom=(b/'MOS.bin').read_bytes();needle=bytes([0xcd])+syms['_main'].to_bytes(3,'little');import re
hits=[m.start() for m in re.finditer(re.escape(needle),rom)];assert len(hits)==1;syms['__warmboot_magic']=hits[0]+4
(b/'symbols-boot.txt').write_text(''.join(f'{v:x} T {k}\n' for k,v in syms.items()))
