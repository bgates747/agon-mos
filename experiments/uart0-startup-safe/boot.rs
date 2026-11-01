//! Execute the linked reset/startup and UART-open code without a board.
//! Flat RAM and register latches model addressing/register writes, not silicon timing.
use ez80::{Cpu, Machine, Reg16};
use std::{collections::{BTreeMap,VecDeque}, env, fs};
const STUB: usize = 0x30000;
const PARAM: usize = 0x31000;
const STACK: u32 = 0xbfff0;
struct Board {
    mem: Vec<u8>, ports: [u8;256], divisor: [u16;2], writes: Vec<(u16,u8)>,
    handshake: bool, wire: Vec<u8>, rx: VecDeque<u8>,
}
impl Board {
    fn new(rom:&[u8])->Self {
        let mut b=Self{mem:vec![0xa5;0x1000000],ports:[0;256],divisor:[0;2],writes:vec![],handshake:false,wire:vec![],rx:VecDeque::new()};
        b.mem[..rom.len()].copy_from_slice(rom); b
    }
    fn set24(&mut self,a:usize,v:u32){for i in 0..3 {self.mem[a+i]=(v>>(8*i))as u8}}
    fn u24(&self,a:usize)->u32{self.mem[a]as u32|((self.mem[a+1]as u32)<<8)|((self.mem[a+2]as u32)<<16)}
}
impl Machine for Board {
    fn peek(&self,a:u32)->u8{self.mem[a as usize]}
    fn poke(&mut self,a:u32,v:u8){self.mem[a as usize]=v}
    fn use_cycles(&self,_:i32){}
    fn port_in(&mut self,p:u16)->u8{
        assert!(p<256,"unexpected port {p:x}");
        if self.handshake {match p {
            0x80=>return self.ports[0x80]|0x80, // Idealized immediate timer expiry.
            0x81|0x82=>return 0, // Counter reaches zero; reload latches remain recorded.
            0xc0=>return self.rx.pop_front().expect("empty RX read"),
            0xc2=>return if self.rx.is_empty(){0xc1}else{0xc4},
            0xc5=>return 0x60|u8::from(!self.rx.is_empty()),
            0xc6=>return 0x10,
            _=>{}
        }}
        self.ports[p as usize]
    }
    fn port_out(&mut self,p:u16,v:u8){
        assert!(p<256,"unexpected port {p:x}");
        self.writes.push((p,v));
        for (n,base) in [0xc0,0xd0].into_iter().enumerate(){
            if self.ports[base+3]&0x80!=0 && (p as usize==base || p as usize==base+1){
                let shift=(p as usize-base)*8;
                self.divisor[n]=(self.divisor[n]&!(255<<shift))|((v as u16)<<shift);return
            }
        }
        if p==0xc0 && self.handshake {
            self.wire.push(v);
            // Byte-level peer deliberately refuses the wrong line speed.
            // It is a minimal boot fixture, not the actual compiled ESP32 VDP.
            if self.divisor[0]==1 {
                if self.wire.ends_with(&[23,0,0x80,1]) {self.rx.extend([0x80,1,1]);}
                if self.wire.ends_with(&[23,0,0x86]) {self.rx.extend([0x86,8,128,2,224,1,80,60,64,0]);}
                if self.wire.ends_with(&[23,0,0x94,128]) {self.rx.extend([0x84,4,0,0,0,0]);}
            }
        }
        self.ports[p as usize]=v;
    }
}
fn symbols(path:&str)->BTreeMap<String,usize>{
    fs::read_to_string(path).unwrap().lines().filter_map(|line|{
        let p:Vec<_>=line.split_whitespace().collect();
        if p.len()==3 {usize::from_str_radix(p[0],16).ok().map(|a|(p[2].into(),a))}else{None}
    }).collect()
}
fn c_call(cpu:&mut Cpu,b:&mut Board,address:usize,arg:Option<u32>){
    cpu.set_adl(true);cpu.state.clear_sz_prefix();cpu.state.halted=false;
    cpu.registers().set24(Reg16::SP,STACK);
    let mut code=vec![];
    if let Some(a)=arg {code.extend([0x21,a as u8,(a>>8)as u8,(a>>16)as u8,0xe5]);}
    code.extend([0xcd,address as u8,(address>>8)as u8,(address>>16)as u8]);
    b.mem[STUB..STUB+code.len()].copy_from_slice(&code);cpu.state.set_pc(STUB as u32);
    for _ in 0..100_000 {
        cpu.execute_instruction(b);
        if cpu.state.pc()==(STUB+code.len())as u32 {
            assert_eq!(cpu.registers().get24(Reg16::SP),STACK-if arg.is_some(){3}else{0});return
        }
    }
    panic!("C function did not return: address={address:x}, pc={:x}",cpu.state.pc())
}
fn reset(rom:&[u8],s:&BTreeMap<String,usize>,warm:bool){
    let mut b=Board::new(rom);let mut cpu=Cpu::new_ez80();
    if warm {b.set24(0xbfffa,s["__warmboot_magic"]as u32);}
    for step in 0..2_000_000 {
        if cpu.state.pc()==s["_main"]as u32 {
            assert!(cpu.registers().adl&&cpu.registers().madl);
            assert!(!cpu.registers().iff1);
            assert_eq!(b.mem[s["__low_data"]..s["__low_data"]+s["__len_data"]],
                       b.mem[s["__low_romdata"]..s["__low_romdata"]+s["__len_data"]]);
            for a in s["__low_bss"]..s["__low_bss"]+s["__len_bss"] {
                if a!=s["_coldBoot"] {assert_eq!(b.mem[a],0,"BSS not cleared at {a:x}");}
            }
            for a in (s["__2nd_jump_table"]..s["__2nd_jump_table"]+48*4).step_by(4){
                assert_eq!(b.mem[a],0xc3);assert_eq!(b.u24(a+1),s["__default_mi_handler"]as u32);
            }
            let bottom=s["__heapbot"];let limit=0xbf800;
            assert!(bottom<limit&&limit+2048==s["__stack"]);
            println!("reset warm_memory={warm} steps={step} main={:x} static_end={bottom:x} heap_limit={limit:x}",s["_main"]);
            return
        }
        cpu.execute_instruction(&mut b);
    }
    panic!("Reset did not reach main: pc={:x}",cpu.state.pc());
}
fn boot_handshake(rom:&[u8],s:&BTreeMap<String,usize>,warm:bool,broken:bool)->bool {
    let mut b=Board::new(rom);b.handshake=true;let mut cpu=Cpu::new_ez80();
    // Simulate incoming retained RAM from a failed experiment. Reset startup
    // must clear it and reinstall stock vectors before communication starts.
    b.mem[s["tx_opened"]]=1;b.mem[s["uart0_initialized"]]=1;
    b.set24(s["__2nd_jump_table"]+0x31,s["tx_isr"]as u32);
    if warm {b.set24(0xbfffa,s["__warmboot_magic"]as u32);}
    if broken {
        // An experimental handler deliberately crashes with interrupts off.
        // Its bad instructions remain in ROM across the subsequent CPU reset.
        let addr=s["tx_isr"];
        b.mem[addr..addr+2].copy_from_slice(&[0xf3,0x76]);
        cpu.set_adl(true);cpu.state.set_pc(addr as u32);
        cpu.execute_instruction(&mut b);cpu.execute_instruction(&mut b);
        assert!(cpu.state.halted);assert!(!cpu.registers().iff1);
        cpu=Cpu::new_ez80();
    }
    let mut entered=false;let mut ei_delay=0;let mut lowest_sp=0xc0000;
    for _ in 0..1_000_000 {
        for name in ["tx_isr","_uart0_tx_init","uart0_activate","read_lsr","read_msr","uart0_pump","uart0_sync_begin","tx_service"] {
            assert_ne!(cpu.state.pc(),s[name]as u32,"experimental routine {name} executed during stock boot");
        }
        if cpu.state.pc()==s["_main"]as u32 {entered=true;}
        if entered {
            lowest_sp=lowest_sp.min(cpu.registers().get24(Reg16::SP));
            assert!(lowest_sp>=0xbf800,"boot stack crossed heap");
        }
        if cpu.state.pc()==s["_bootmsg"]as u32 {
            assert_eq!(b.divisor[0],1);assert_eq!(b.mem[s["_gp"]],1);
            assert_eq!(b.mem[s["_scrcolours"]],64);assert_eq!(b.mem[s["_scrpixelIndex"]],0);
            assert_eq!(b.u24(s["__2nd_jump_table"]+0x30+1),s["_uart0_handler"]as u32);
            assert_eq!((b.ports[0x82]as u16)*256+b.ports[0x81]as u16,11520);
            if s.contains_key("tx_opened") {
                assert_eq!(b.mem[s["tx_opened"]],0);assert_eq!(b.mem[s["tx_cts_batch"]],0);
                assert_eq!(b.mem[s["uart0_initialized"]],0);
                assert_eq!(b.mem[s["tx_rx_errors"]],0);
            }
            println!("boot handshake_pass=true warm={warm} crashed_experiment={broken} divisor=1 GP=1 mode=64 palette=0 minimum_SP={lowest_sp:x} timer_reload=11520");return true
        }
        let op=b.mem[cpu.state.pc()as usize];cpu.execute_instruction(&mut b);
        if op==0xfb {ei_delay=1;continue}
        if ei_delay>0 {ei_delay-=1;}
        if ei_delay==0 && cpu.registers().iff1 && b.ports[0xc1]&1!=0 && !b.rx.is_empty() {
            let pc=cpu.state.pc();let sp=cpu.registers().get24(Reg16::SP);
            let saved:[u32;6]=[Reg16::AF,Reg16::BC,Reg16::DE,Reg16::HL,Reg16::IX,Reg16::IY].map(|r|if r==Reg16::AF {cpu.registers().get16(r)as u32}else{cpu.registers().get24(r)});
            b.set24((sp-3)as usize,pc);b.mem[(sp-4)as usize]=1;
            cpu.registers().set24(Reg16::SP,sp-4);cpu.registers().iff1=false;cpu.registers().iff2=false;
            cpu.state.set_pc(s["_uart0_handler"]as u32);
            let mut returned=false;
            for _ in 0..10_000 {cpu.execute_instruction(&mut b);lowest_sp=lowest_sp.min(cpu.registers().get24(Reg16::SP));assert!(lowest_sp>=0xbf800);if cpu.state.pc()==pc {returned=true;break}}
            assert!(returned,"boot RX ISR hung");assert_eq!(cpu.registers().get24(Reg16::SP),sp);
            for (r,v) in [Reg16::AF,Reg16::BC,Reg16::DE,Reg16::HL,Reg16::IX,Reg16::IY].into_iter().zip(saved){let actual=if r==Reg16::AF {cpu.registers().get16(r)as u32}else{cpu.registers().get24(r)};assert_eq!(actual,v,"boot RX clobbered {r:?}");}
        }
    }
    assert!(entered,"boot did not reach main");
    println!("boot handshake_pass=false divisor={} GP={} wire_bytes={} PC={:x}",b.divisor[0],b.mem[s["_gp"]],b.wire.len(),cpu.state.pc());false
}
fn main(){
    let a:Vec<_>=env::args().collect();let rom=fs::read(&a[1]).unwrap();let s=symbols(&a[2]);
    let mut all=true;
    // The overflowing rate and a nearby control are essential; lower rates alone miss it.
    for baud in [9600u32,115200,384000,576000,921600,1048576,1152000] {
        for n in 0..2 {
            let mut b=Board::new(&rom);let mut cpu=Cpu::new_ez80();
            b.set24(PARAM,baud);b.mem[PARAM+3..PARAM+8].copy_from_slice(&[8,1,0,1,1]);
            c_call(&mut cpu,&mut b,s[if n==0{"_open_UART0"}else{"_open_UART1"}],Some(PARAM as u32));
            let expected=18_432_000u32/(16*baud);let actual=b.divisor[n];
            let base=if n==0{0xc0}else{0xd0};
            let pass=actual as u32==expected&&b.ports[base+3]==3&&b.ports[base+1]==1;
            all&=pass;
            println!("UART{n} baud={baud} divisor={actual} expected={expected} LCTL={} IER={} pass={pass}",b.ports[base+3],b.ports[base+1]);
        }
    }
    reset(&rom,&s,false);reset(&rom,&s,true);
    for warm in [false,true] {for broken in [false,true] {all&=boot_handshake(&rom,&s,warm,broken);}}
    if !all {std::process::exit(1)}
}
