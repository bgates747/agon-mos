"""Prepare actual-ROM oracle sources; builds/runs take place only on Oryx."""
import hashlib,sys
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=Path(sys.argv[1]).resolve();out=b/'oracle';(out/'src').mkdir(parents=True,exist_ok=False)
source=root/'build/uart0-batching/runner/src/main.rs'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9aa4e2011e4573f4ed92611b7ab505ca72d8ef21ef43081b7c8e1c58afb1200a'
s=source.read_text().split('fn main(){')[0]
s=s.replace('u.set24(s["tx_next_ticket"],1);','u.set24(s["tx_next_ticket"],1);let vector=s["__2nd_jump_table"]+0x30;u.mem[vector]=0xc3;u.set24(vector+1,s["_uart0_handler"]as u32);')
s=s.replace('assert!(steps<1_000_000,"API hung: {name}");','assert!(steps<8_000_000,"API hung: {name} pc={:x} source={:x} remaining={:x} mode={}",self.cpu.state.pc(),self.word("tx_write_source"),self.word("tx_write_count"),self.byte("tx_write_mode"));')
s=s.replace('ei_delay:u8}', 'ei_delay:u8,callbacks:Vec<(u32,u32,u8,bool)>}')
s=s.replace('inject_api:false,ei_delay:0}', 'inject_api:false,ei_delay:0,callbacks:vec![]}')
s=s.replace('fn step(&mut self){self.cpu.execute_instruction', 'fn step(&mut self){if self.cpu.state.pc()==CALLBACK as u32 {self.callbacks.push((self.cpu.registers().get24(Reg16::HL),self.cpu.registers().get24(Reg16::DE),self.cpu.registers().a(),self.cpu.registers().iff1));}self.cpu.execute_instruction')
(out/'src/main.rs').write_text(s+(root/'experiments/uart0-completion/tests.rs').read_text())
(out/'Cargo.toml').write_text('[package]\nname="uart0-completion-oracle"\nversion="0.1.0"\nedition="2021"\n[dependencies]\nez80={path="'+str(root/'build/uart0-async/ez80-model')+'"}\n')
