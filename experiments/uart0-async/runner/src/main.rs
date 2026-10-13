//! Executes the real assembled driver against an independent, deterministic UART.
//! Acknowledge/vector delivery is injected, not supplied by this CPU crate.
//! UART timing is idealized (160 host cycles per 8N1 byte), never silicon evidence.
use ez80::{Cpu, Machine, Reg16};
use std::{cell::Cell, collections::{BTreeMap, VecDeque}, env, fs};
const CODE: usize = 0x40000;
const STUB: usize = 0x30000;
const STACK: u32 = 0xbfff0;
const SOURCE: usize = 0x5fff8;
const RAM: usize = 0x1000000;

struct Uart {
    mem: Vec<u8>, time: Cell<i64>, last: i64, char_cycles: i64,
    fifo: VecDeque<u8>, shift: Option<(u8,i64)>, wire: Vec<u8>, writes: Vec<u8>,
    ier: u8, tx_pending: bool, cts: bool, delta: u8, errors: u8, rx: VecDeque<u8>, rx_read: Vec<u8>,
    last_sample: bool, cut: Option<usize>, events: BTreeMap<usize,bool>, io: usize,
    admission: usize, admitted: bool, max_fifo: usize, iirs: Vec<u8>,
    rx_timeout: bool, inject_unknown: bool, trace: Vec<String>,
    arrivals: VecDeque<(i64,u8)>, rx_lost: usize, max_rx_fifo: usize, wire_done:i64,
}
impl Uart {
    fn new(image: &[u8]) -> Self {
        let mut s=Self { mem: vec![0;RAM],time:Cell::new(0),last:0,char_cycles:160,
            fifo:VecDeque::new(),shift:None,wire:vec![],writes:vec![],ier:1,tx_pending:false,cts:true,
            delta:0,errors:0,rx:VecDeque::new(),rx_read:vec![],last_sample:false,cut:None,
            events:BTreeMap::new(),io:0,admission:0,admitted:false,max_fifo:0,iirs:vec![],
            rx_timeout:false,inject_unknown:false,trace:vec![],arrivals:VecDeque::new(),rx_lost:0,max_rx_fifo:0,wire_done:0 };
        s.mem[CODE..CODE+image.len()].copy_from_slice(image); s
    }
    fn sync(&mut self) {
        let now=self.time.get();
        while let Some((byte,done))=self.shift {
            if done>now {break}
            self.wire.push(byte);self.wire_done=done;
            let next=self.fifo.pop_front();
            if next.is_some()&&self.fifo.is_empty(){self.tx_pending=true;}
            self.shift=next.map(|v|(v,done+self.char_cycles));
        }
        while let Some(&(at,byte))=self.arrivals.front(){
            if at>now{break}
            self.arrivals.pop_front();
            if self.rx.len()==16{self.rx_lost+=1;self.errors|=2}else{self.rx.push_back(byte)}
            self.max_rx_fifo=self.max_rx_fifo.max(self.rx.len());
        }
        self.last=now;

    }
    fn advance(&mut self,n:i64){self.time.set(self.time.get()+n);self.sync()}
    fn edge(&mut self,ready:bool){if self.cts!=ready{self.cts=ready;self.delta|=1}}
    fn cause(&self)->u8 {
        if self.inject_unknown {return 0xca}
        if self.ier&4!=0 && self.errors!=0 {0xc6}
        else if self.ier&1!=0 && !self.rx.is_empty(){if self.rx_timeout{0xcc}else{0xc4}}
        else if self.ier&2!=0 && self.tx_pending {0xc2}
        else if self.ier&8!=0 && self.delta!=0 {0xc0}
        else{0xc1}
    }
    fn pending(&mut self)->bool{self.sync();self.cause()&1==0}
    fn before_io(&mut self,name:&str) {
        self.sync();self.io+=1;
        if let Some(ready)=self.events.remove(&self.io){self.edge(ready)}
        if let Some(cut)=self.cut{if self.writes.len()>=cut{self.edge(false)}}
        if self.trace.len()<1000 {self.trace.push(format!("{}:{}",self.io,name))}
    }
    fn u24(&self,a:usize)->u32{self.mem[a]as u32|((self.mem[a+1]as u32)<<8)|((self.mem[a+2]as u32)<<16)}
    fn set24(&mut self,a:usize,v:u32){for i in 0..3{self.mem[a+i]=(v>>(i*8))as u8}}
}
impl Machine for Uart {
    fn peek(&self,a:u32)->u8{self.time.set(self.time.get()+1);self.mem[a as usize]}
    fn poke(&mut self,a:u32,v:u8){self.time.set(self.time.get()+1);self.mem[a as usize]=v}
    fn use_cycles(&self,n:i32){self.time.set(self.time.get()+n as i64)}
    fn port_in(&mut self,p:u16)->u8 {
        self.before_io(&format!("in {p:x}"));
        match p {
            0xc0=>{let v=self.rx.pop_front().expect("RX read without data");self.rx_read.push(v);v}
            0xc1=>self.ier,
            0xc2=>{let v=self.cause();self.iirs.push(v);if v&0xf==2{self.tx_pending=false;}v}
            0xc5=>{let empty=self.fifo.is_empty();if empty{self.admitted=true;self.admission=0}
                let v=self.errors|u8::from(!self.rx.is_empty())|if empty{32}else{0}|
                    if empty&&self.shift.is_none(){64}else{0};self.errors=0;v}
            0xc6=>{self.last_sample=self.cts;let v=if self.cts{16}else{0}|self.delta;self.delta=0;v}
            _=>panic!("unexpected port read {p:x}"),
        }
    }
    fn port_out(&mut self,p:u16,v:u8){
        self.before_io(&format!("out {p:x} {v:x}"));
        match p {
            0xc0=>{
                assert!(self.last_sample,"CTS guard missing");
                assert!(self.admitted,"write without empty-FIFO admission");
                self.admission+=1; assert!(self.admission<=16,"burst exceeds 16");
                assert!(self.fifo.len()<16,"FIFO overflow");
                self.writes.push(v);
                self.tx_pending=false;
                if self.shift.is_none(){self.shift=Some((v,self.time.get()+self.char_cycles));self.tx_pending=true;}
                else{self.fifo.push_back(v)}
                self.max_fifo=self.max_fifo.max(self.fifo.len());
            },
            0xc1=>{assert_eq!(v&0xf0,0,"unsupported IER bits");
                if v&2!=0&&self.ier&2==0&&self.fifo.is_empty(){self.tx_pending=true;}
                self.ier=v},
            _=>panic!("unexpected port write {p:x}"),
        }
    }
}
struct Rig {cpu:Cpu,u:Uart,s:BTreeMap<String,usize>,isr_count:usize,isr_cycles:i64,
    max_isr_steps:usize,max_isr_writes:usize,max_isr_rx:usize, guard:bool, inject_api:bool, ei_delay:u8}
impl Rig {
    fn new(image:&[u8],s:&BTreeMap<String,usize>)->Self{
        let production=s.contains_key("uart0_sync_depth"); let mut cpu=Cpu::new_ez80();cpu.set_adl(true);cpu.registers().set24(Reg16::SP,STACK);cpu.registers().set16(Reg16::SP,0x8765);
        cpu.registers().madl=true;cpu.registers().mbase=if production{0}else{0x53};cpu.registers().iff1=true;cpu.registers().iff2=true;
        let mut u=Uart::new(image); if production { u.mem.fill(0);u.mem[..image.len()].copy_from_slice(image);let data=u.mem[s["__low_romdata"]..s["__low_romdata"]+s["__len_data"]].to_vec();u.mem[s["__low_data"]..s["__low_data"]+data.len()].copy_from_slice(&data);u.mem[s["_serialFlags"]]=3;u.set24(s["tx_next_ticket"],1); } Self{cpu,u,s:s.clone(),isr_count:0,isr_cycles:0,max_isr_steps:0,
            max_isr_writes:0,max_isr_rx:0,guard:true,inject_api:false,ei_delay:0}
    }
    fn at(&self,n:&str)->usize{self.s[n]}
    fn byte(&self,n:&str)->u8{self.u.mem[self.at(n)]}
    fn word(&self,n:&str)->u32{self.u.u24(self.at(n))}
    fn snapshot(&mut self)->Vec<u32>{
        let mut v=vec![];for r in [Reg16::AF,Reg16::BC,Reg16::DE,Reg16::HL,Reg16::IX,Reg16::IY,Reg16::SP] {
            v.push(if r==Reg16::AF {self.cpu.registers().get16(r)as u32}else{self.cpu.registers().get24(r)});
        }v
    }
    fn step(&mut self){self.cpu.execute_instruction(&mut self.u);self.u.sync()}
    fn irq(&mut self){
        assert!(self.cpu.registers().iff1,"IRQ during DI");
        let old_pc=self.cpu.state.pc();let old_sp=self.cpu.registers().get24(Reg16::SP);
        let regs=self.snapshot();let mb=self.cpu.registers().mbase;
        let ss=self.cpu.registers().get16(Reg16::SP);
        let before=self.u.time.get();let nw=self.u.writes.len();let nr=self.u.rx_read.len();
        let ni=self.u.iirs.len();
        // CPU crate exposes no maskable interrupt input. Inject documented
        // mixed-mode ADL frame (mode byte + 24-bit PC), IFF clearing and vector
        // entry, then execute ISR. RETI.L consumes all four bytes.
        self.u.set24((old_sp-3)as usize,old_pc);
        self.u.mem[(old_sp-4)as usize]=1;
        self.cpu.registers().set24(Reg16::SP,old_sp-4);
        self.cpu.registers().iff1=false;self.cpu.registers().iff2=false;
        self.cpu.state.halted=false;self.cpu.state.set_pc(self.at("tx_isr")as u32);
        self.u.advance(8); // explicitly assumed acknowledge tax, not calibrated
        let mut steps=0;
        loop{
            self.step();steps+=1;
            assert!(steps<4000,"unbounded ISR");
            if self.cpu.state.pc()==old_pc{break}
        }
        assert_eq!(self.snapshot(),regs,"ISR register/stack damage");
        assert_eq!(self.cpu.registers().mbase,mb);assert!(self.cpu.registers().adl);
        assert_eq!(self.cpu.registers().get16(Reg16::SP),ss);
        assert!(self.cpu.registers().iff1&&self.cpu.registers().iff2);
        let writes=self.u.writes.len()-nw;let rx=self.u.rx_read.len()-nr;
        assert!(writes<=16,"ISR TX budget exceeded");assert!(rx<=16,"ISR RX budget exceeded");
        assert!(self.u.iirs.len()-ni<=8,"ISR cause budget exceeded");
        self.max_isr_steps=self.max_isr_steps.max(steps);
        self.max_isr_writes=self.max_isr_writes.max(writes);self.max_isr_rx=self.max_isr_rx.max(rx);
        self.isr_count+=1;self.isr_cycles+=self.u.time.get()-before;
    }
    fn maybe_irq(&mut self){if self.cpu.registers().iff1&&self.u.pending(){self.irq()}}
    fn call(&mut self,name:&str,de:u32,hl:u32,bc:u32)->(u8,u32,u8){
        self.cpu.state.halted=false;self.cpu.state.clear_sz_prefix();
        self.cpu.registers().set24(Reg16::DE,de);self.cpu.registers().set24(Reg16::HL,hl);
        self.cpu.registers().set24(Reg16::BC,bc);
        let addr=self.at(name)as u32;
        self.u.mem[STUB..STUB+5].copy_from_slice(&[0xcd,addr as u8,(addr>>8)as u8,(addr>>16)as u8,0]);
        self.cpu.state.set_pc(STUB as u32);
        let mb=self.cpu.registers().mbase;let iff=self.cpu.registers().iff1;assert_eq!(iff,self.cpu.registers().iff2);
        let sp=self.cpu.registers().get24(Reg16::SP);let short_sp=self.cpu.registers().get16(Reg16::SP);
        let ix=self.cpu.registers().get24(Reg16::IX);let iy=self.cpu.registers().get24(Reg16::IY);
        let mut steps=0;
        while self.cpu.state.pc()!=STUB as u32+4 {
            let opcode=self.u.mem[self.cpu.state.pc()as usize];
            self.step();steps+=1;assert!(steps<1_000_000,"API hung: {name}");
            if self.inject_api{
                if opcode==0xfb{self.ei_delay=1}
                else{
                    if self.ei_delay>0{self.ei_delay-=1}
                    if self.ei_delay==0{self.maybe_irq()}
                }
            }

            // Don't inject in the EI/RET delay slot; model EI has no delay.
            // Calls are DI internally; boundary race delivery is tested separately.
        }
        assert_eq!(self.cpu.registers().iff1,iff,"{name} changed IFF1");
        assert_eq!(self.cpu.registers().iff2,iff,"{name} changed IFF2");
        assert_eq!(self.cpu.registers().get24(Reg16::SP),sp);
        assert_eq!(self.cpu.registers().get16(Reg16::SP),short_sp);
        assert_eq!(self.cpu.registers().get24(Reg16::IX),ix);
        assert_eq!(self.cpu.registers().get24(Reg16::IY),iy);
        assert_eq!(self.cpu.registers().mbase,mb);assert!(self.cpu.registers().adl);
        (self.cpu.registers().a(),self.cpu.registers().get24(Reg16::HL),
            (self.cpu.registers().get16(Reg16::BC)>>8)as u8)
    }
    fn open(&mut self){assert_eq!(self.call("tx_open",0,0,0).0,0)}
    fn reserve(&mut self)->u32{let(r,t,_)=self.call("tx_reserve",0,0,0);assert_eq!(r,0);assert_ne!(t,0);t}
    fn publish(&mut self,t:u32,addr:usize,bytes:&[u8]){
        self.u.mem[addr..addr+bytes.len()].copy_from_slice(bytes);
        assert_eq!(self.call("tx_publish",t,addr as u32,bytes.len()as u32).0,0);
    }
    fn state(&mut self,t:u32)->(u8,u32){let(r,n,s)=self.call("tx_status",t,0,0);assert_eq!(r,0);(s,n)}
    fn settle(&mut self){
        for _ in 0..100_000{
            self.u.advance(160);
            if self.u.pending(){self.irq()}
            if self.word("tx_head")==0&&self.u.shift.is_none()&&self.u.fifo.is_empty(){return}
        }panic!("failed to drain head={:x} ier={:x} cts={} shift={:?} fifo={} writes={}",self.word("tx_head"),self.u.ier,self.u.cts,self.u.shift,self.u.fifo.len(),self.u.writes.len())
    }
    fn assert_queue(&self){
        if !self.guard{return}
        let mut seen=vec![];let mut p=self.word("tx_head")as usize;
        while p!=0{
            assert!(seen.len()<3&&!seen.contains(&p),"bad queue links");seen.push(p);
            assert!((self.at("tx_slots")..self.at("tx_slots")+57).contains(&p));
            assert_eq!((p-self.at("tx_slots"))%19,0);
            assert!([2,3].contains(&self.u.mem[p]));
            assert_eq!(self.u.u24(p+7)+self.u.u24(p+10),self.u.u24(p+13));p=self.u.u24(p+16)as usize;
        }
        assert_eq!(self.word("tx_tail")as usize,*seen.last().unwrap_or(&0));
    }
}
fn payload(n:usize,seed:u8)->Vec<u8>{(0..n).map(|i|(i as u8).wrapping_mul(157).wrapping_add(seed)).collect()}
fn basic(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for len in [1,2,15,16,17,31,32,33,255,256,257,6720,65535]{
        for iff in [false,true]{
            let mut r=Rig::new(image,s);r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
            assert_eq!(r.call("tx_reserve",0,0,0).0,3);r.open();
            assert_eq!(r.call("tx_open",0,0,0).0,1);
            let t=r.reserve();let data=payload(len,7);r.publish(t,SOURCE,&data);
            // settle() is an IRQ-driven fixture; turn on interrupts explicitly
            // after confirming every foreground call preserved disabled IFF.
            r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;
            r.settle();assert_eq!(r.u.wire,data);assert_eq!(r.state(t),(4,len as u32));
            assert_eq!(r.call("tx_close",0,0,0).0,1);
            assert_eq!(r.call("tx_reap",t,0,0).0,0);assert_eq!(r.call("tx_status",t,0,0).0,2);
            assert_eq!(r.call("tx_poll_drain",0,0,0).0,0);assert_eq!(r.call("tx_close",0,0,0).0,0);
            assert_eq!(r.u.ier,1);assert!(!r.u.pending());cases+=1;
        }
    }
    cases
}
fn address_width(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for value in [0,1,0x10000,0x800000,0xffffff]{
        let mut r=Rig::new(image,s);
        r.call("hl_zero",0x123456,value,0);
        let zero=r.cpu.registers().get16(Reg16::AF)&0x40!=0;
        assert_eq!(zero,value==0);assert_eq!(r.cpu.registers().get24(Reg16::HL),value);
        assert_eq!(r.cpu.registers().get24(Reg16::DE),0x123456);cases+=1;
    }
    cases
}
fn ownership(image:&[u8],s:&BTreeMap<String,usize>)->usize{

    let mut r=Rig::new(image,s);r.open();r.u.edge(false);
    let a=r.reserve();let b=r.reserve();let c=r.reserve();assert_eq!(r.call("tx_reserve",0,0,0).0,1);
    // Publication defines order, not reservation order.
    r.publish(b,SOURCE,&payload(33,2));r.publish(a,SOURCE+128,&payload(17,3));
    r.publish(c,SOURCE+256,&payload(8,4));r.assert_queue();
    assert_eq!(r.call("tx_cancel",a,0,0).0,0);r.assert_queue(); // middle unlink
    assert_eq!(r.call("tx_reap",a,0,0).0,0);
    let d=r.reserve();assert_ne!(a,d);assert_eq!(r.state(d),(1,0));
    assert_eq!(r.call("tx_publish",d,0xfffff8,17).0,2);
    assert_eq!(r.call("tx_publish",d,SOURCE as u32,0).0,2);
    assert_eq!(r.call("tx_publish",d,SOURCE as u32,65536).0,2);
    assert_eq!(r.call("tx_status",a,0,0).0,2);
    assert_eq!(r.call("tx_cancel",c,0,0).0,0);r.assert_queue(); // tail unlink
    assert_eq!(r.call("tx_cancel",b,0,0).0,0);r.assert_queue(); // sole/head unlink
    assert_eq!(r.u.ier&10,0);assert!(r.u.writes.is_empty());
    for t in [b,c]{assert_eq!(r.call("tx_reap",t,0,0).0,0)}
    assert_eq!(r.call("tx_cancel",d,0,0).0,0);assert_eq!(r.call("tx_reap",d,0,0).0,0);
    r.u.edge(true);r.u.char_cycles=1000;let t=r.reserve();r.publish(t,SOURCE,&[0x42]);
    assert_eq!(r.state(t),(4,1));assert_eq!(r.call("tx_poll_drain",0,0,0).0,1);
    // Source may be mutated immediately on release; the UART holds a copy.
    r.u.mem[SOURCE]=0xff;r.settle();assert_eq!(r.u.wire,[0x42]);
    assert_eq!(r.call("tx_reap",t,0,0).0,0);
    // Exhaustion never silently wraps across sessions.
    r.u.set24(r.at("tx_next_ticket"),0xffffff);let last=r.reserve();assert_eq!(last,0xffffff);
    assert_eq!(r.call("tx_reserve",0,0,0).0,1);
    assert_eq!(r.call("tx_cancel",last,0,0).0,0);assert_eq!(r.call("tx_reap",last,0,0).0,0);
    assert_eq!(r.call("tx_close",0,0,0).0,0);r.open();assert_eq!(r.call("tx_reserve",0,0,0).0,1);
    1
}
fn stalls(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for cut in 0..=34{
        let mut r=Rig::new(image,s);r.open();let t=r.reserve();r.u.cut=Some(cut);
        let data=payload(40,5);r.publish(t,SOURCE,&data);
        for _ in 0..100 {r.u.advance(160);r.maybe_irq()}
        assert_eq!(r.u.writes.len(),cut);assert_eq!(r.state(t).1,cut as u32);
        assert_eq!(r.call("tx_close",0,0,0).0,1,"stalled exit released pending sources");
        assert_eq!(r.call("tx_cancel",t,0,0).0,if cut==0{0}else{1});
        if cut==0{cases+=1;continue}
        let idle=r.isr_count;for _ in 0..100{r.u.advance(160);r.maybe_irq()}
        assert_eq!(r.isr_count,idle,"CTS-blocked IRQ storm");assert_eq!(r.u.ier&2,0);
        r.u.cut=None;r.u.edge(true);r.settle();assert_eq!(r.u.wire,data);cases+=1;
    }
    // Move a low/high CTS edge across every IO boundary of initial publication.
    for event in 1..=50{
        for width in [1,2,3,9]{
            let mut r=Rig::new(image,s);r.open();let t=r.reserve();let base=r.u.io;
            r.u.events.insert(base+event,false);r.u.events.insert(base+event+width,true);
            r.publish(t,SOURCE,&payload(64,13));
            for _ in 0..2000{
                r.u.advance(160);r.maybe_irq();
                // If no later I/O occurs, the scheduled external edge still
                // happens; do not make a wakeup depend on the CPU reading MSR.
                if !r.u.cts&&!r.u.pending(){r.u.events.clear();r.u.edge(true)}
                if r.word("tx_head")==0&&r.u.shift.is_none(){break}
            }
            r.u.events.clear();r.u.edge(true);r.settle();assert_eq!(r.u.wire,payload(64,13));cases+=1;
        }
    }
    cases
}
fn reception(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for errors in [0,2,4,8,16,128,0x9e]{
        for timeout in [false,true]{
            let mut r=Rig::new(image,s);r.open();r.u.edge(false);let t=r.reserve();
            r.publish(t,SOURCE,&payload(128,9));r.u.rx_timeout=timeout;r.u.errors=errors;
            let data=payload(16,99);r.u.rx.extend(data.clone());
            let callback=r.at("rx_callback_test");r.u.mem[callback]=1;
            let before=r.u.writes.len();r.maybe_irq();assert_eq!(r.u.rx_read,data);
            assert_eq!(r.u.writes.len(),before);assert_eq!(r.byte("tx_rx_errors"),errors);
            assert_eq!(r.byte("rx_callback_status"),4);assert_eq!(r.word("rx_count"),16);
            let count=r.isr_count;for _ in 0..100{r.u.advance(160);r.maybe_irq()}
            assert_eq!(r.isr_count,count);r.u.edge(true);r.settle();assert_eq!(r.u.wire,payload(128,9));
            assert_eq!(r.word("rx_count"),16,"TX/modem fabricated RX data");cases+=1;
        }
    }
    let mut r=Rig::new(image,s);r.open();let pc=r.cpu.state.pc();r.irq();assert_eq!(r.cpu.state.pc(),pc);
    assert!(r.u.rx_read.is_empty());assert_eq!(r.u.iirs.last(),Some(&0xc1));
    r.u.inject_unknown=true;r.irq();assert_eq!(r.byte("tx_unknown_cause"),10);
    assert!(r.u.rx_read.is_empty());cases+2
}
fn duplex(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for spacing in [160,320,640]{
        let mut r=Rig::new(image,s);r.open();let t=r.reserve();
        let rx=payload(256,57);let now=r.u.time.get();
        for (i,&b) in rx.iter().enumerate(){r.u.arrivals.push_back((now+100+(i as i64)*spacing,b))}
        r.publish(t,SOURCE,&payload(1024,18));
        for _ in 0..200000{
            r.u.advance(8);r.maybe_irq();
            if r.word("tx_head")==0&&r.u.shift.is_none()&&r.u.arrivals.is_empty()&&r.u.rx.is_empty(){break}
        }
        assert_eq!(r.u.rx_lost,0,"RX overrun at spacing {spacing}");
        assert_eq!(r.u.rx_read,rx);assert_eq!(r.u.wire,payload(1024,18));
        assert_eq!(r.word("rx_count"),256);assert_eq!(r.byte("rx_overflow"),0);
        assert!(r.max_isr_rx<=16);assert!(r.max_isr_writes<=16);cases+=1;
    }
    cases
}
fn registers(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for mb in [0,7,8,0x53]{
        for flags in 0..256u16{
            let mut r=Rig::new(image,s);r.open();r.u.edge(false);let t=r.reserve();
            r.publish(t,SOURCE,&payload(64,9));
            // Seed the shadow bank using real exchange instructions.
            r.u.mem[STUB+16..STUB+20].copy_from_slice(&[0xd9,0x08,0xd9,0x08]);
            r.cpu.state.set_pc((STUB+16)as u32);r.step();r.step();
            for(reg,v)in [(Reg16::BC,0x123456),(Reg16::DE,0x789abc),(Reg16::HL,0xdef012)]{r.cpu.registers().set24(reg,v)}
            r.cpu.registers().set16(Reg16::AF,0x5a00|flags);r.step();r.step();
            r.cpu.registers().set16(Reg16::AF,0xa500|flags);
            for(reg,v)in [(Reg16::BC,0x654321),(Reg16::DE,0xcba987),(Reg16::HL,0x210fed),(Reg16::IX,0x112233),(Reg16::IY,0x445566)]{r.cpu.registers().set24(reg,v)}
            r.cpu.registers().mbase=mb;r.u.edge(true);r.irq();
            r.cpu.state.set_pc((STUB+16)as u32);r.step();r.step();
            for(reg,v)in [(Reg16::BC,0x123456),(Reg16::DE,0x789abc),(Reg16::HL,0xdef012)]{assert_eq!(r.cpu.registers().get24(reg),v)}
            assert_eq!(r.cpu.registers().get16(Reg16::AF),0x5a00|flags);
            assert_eq!(r.cpu.registers().mbase,mb);assert!(r.cpu.registers().madl);cases+=1;
        }
    }cases
}
fn barrier(image:
&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut r=Rig::new(image,s);r.open();let a=r.reserve();let b=r.reserve();
    let data=payload(64,31);r.publish(a,SOURCE,&data);
    assert_eq!(r.call("tx_barrier_enter",0,0,0).0,0);
    assert_eq!(r.call("tx_barrier_enter",0,0,0).0,1);
    assert_eq!(r.call("tx_publish",b,SOURCE as u32,1).0,1);
    assert_eq!(r.call("tx_sync_byte",b'!' as u32,0,0).0,1,"ordinary output interleaved");
    r.settle();assert_eq!(r.call("tx_sync_byte",b'!' as u32,0,0).0,0);
    r.settle();let mut want=data;want.push(b'!');assert_eq!(r.u.wire,want);
    assert_eq!(r.call("tx_barrier_leave",0,0,0).0,0);
    r.publish(b,SOURCE+256,&[0x66]);r.settle();assert_eq!(r.u.wire.last(),Some(&0x66));
    assert_eq!(r.call("tx_cancel",a,0,0).0,1);1
}
fn random_queue(image:&[u8],s:&BTreeMap<String,usize>)->usize{
    let mut cases=0;
    for seed in 1..=100u64{
        let mut rnd=seed;let mut next=||{rnd^=rnd<<13;rnd^=rnd>>7;rnd^=rnd<<17;rnd};
        let mut r=Rig::new(image,s);r.open();r.inject_api=true;let mut live:Vec<(u32,usize,Vec<u8>,bool)>=vec![];
        let mut expected=vec![];
        for step in 0..300{
            let choice=next()%6;
            if choice==0&&live.len()<3{
                let t=r.reserve();let ix=r.at("tx_slots")+(0..3).find(|i|r.u.u24(r.at("tx_slots")+i*19+1)==t).unwrap()*19;
                let addr=SOURCE+(ix-r.at("tx_slots"))/19*512;
                live.push((t,addr,payload((next()%180+1)as usize,step as u8),false));
            } else if choice==1{
                if let Some(x)=live.iter_mut().find(|x|!x.3){r.publish(x.0,x.1,&x.2);expected.extend(&x.2);x.3=true}
            } else if choice==2{r.u.edge(next()&1==0)}
            else if choice==3{r.u.advance((next()%1200)as i64);r.maybe_irq()}
            else if choice==4 {assert_eq!(r.call("tx_kick",0,0,0).0,0)}
            else if let Some(i)=live.iter().position(|x|r.u.mem[(0..3).map(|j|r.at("tx_slots")+j*19).find(|&p|r.u.u24(p+1)==x.0).unwrap()]==4){
                let(t,a,_,_)=live.remove(i);assert_eq!(r.call("tx_reap",t,0,0).0,0);r.u.mem[a..a+256].fill(0xee);
            }
            r.assert_queue();
        }
        r.u.edge(true);r.settle();assert_eq!(r.u.wire,expected,"seed {seed}");cases+=1;
    }cases
}
fn packet(seed:u8)->Vec<u8>{
    let id=0x1200u16+seed as u16;let data=payload(512,seed);
    let mut p=vec![23,0,0xa0,id as u8,(id>>8)as u8,2,23,0,0xa0,id as u8,(id>>8)as u8,0,0,2];
    p.extend(data);p
}
fn parse_packets(wire:&[u8]){
    let mut p=0;
    for seed in 0..3{
        let want=packet(seed);assert_eq!(&wire[p..p+want.len()],want);p+=want.len();
    }assert_eq!(p,wire.len());
}
fn benchmark(image:&[u8],s:&BTreeMap<String,usize>,async_mode:bool,mask:usize)->(i64,i64,usize,usize,usize,i64,i64){
    let mut r=Rig::new(image,s);r.open();let start=r.u.time.get();let mut tickets=vec![];
    for seed in 0..3{
        let p=packet(seed);let addr=SOURCE+seed as usize*1024;
        if async_mode{let t=r.reserve();r.publish(t,addr,&p);tickets.push(t)}
        else{r.u.mem[addr..addr+p.len()].copy_from_slice(&p);assert_eq!(r.call("blocking_send",0,addr as u32,p.len()as u32).0,0)}
    }
    r.cpu.registers().set24(Reg16::BC,20000);r.cpu.registers().set24(Reg16::HL,0);
    r.cpu.state.halted=false;r.cpu.state.set_pc(r.at("producer")as u32);
    let mut useful=0;let mut overlap=0;let mut ticks=0;
    let mut mask_start=r.u.time.get();let mut max_mask_cycles=0;
    if async_mode&&mask>0{r.cpu.registers().iff1=false;r.cpu.registers().iff2=false}

    while r.cpu.state.pc()!=r.at("producer_done")as u32{
        let pc=r.cpu.state.pc();
        if pc==r.at("producer_tick")as u32{
            useful+=1;if r.u.shift.is_some()||!r.u.fifo.is_empty(){overlap+=1}
        }
        r.step();ticks+=1;
        if async_mode&&(mask==0||ticks%mask==0){
            if mask>0{max_mask_cycles=max_mask_cycles.max(r.u.time.get()-mask_start)}
            r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.maybe_irq();
            mask_start=r.u.time.get();
            if mask>0{r.cpu.registers().iff1=false;r.cpu.registers().iff2=false}
        }

    }
    assert_eq!(useful,20000);assert_eq!(r.cpu.registers().get24(Reg16::HL),20000);
    if async_mode&&mask>0{max_mask_cycles=max_mask_cycles.max(r.u.time.get()-mask_start)}
    r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;
    r.settle();parse_packets(&r.u.wire);

    for t in tickets{assert_eq!(r.state(t).0,4);assert_eq!(r.call("tx_reap",t,0,0).0,0)}
    assert_eq!(r.call("tx_close",0,0,0).0,0);assert_eq!(r.u.ier,1);assert!(!r.u.pending());
    (r.u.time.get()-start,r.isr_cycles,overlap,r.isr_count,r.u.wire.len(),max_mask_cycles,r.u.wire_done-start)
}
fn negative_controls(image:&[u8],s:&BTreeMap<String,usize>){
    if let Ok(mode)=env::var("UART_NEGATIVE"){
        let mut changed=image.to_vec();
        if mode=="cts"{
            // BIT 4,A / JR Z in service_next. Force the branch not to execute.
            let start=s["service_next"]-CODE;
            assert_eq!(&changed[start+4..start+6],&[0xcb,0x67]);
            assert_eq!(changed[start+6],0x28);changed[start+6]=0;changed[start+7]=0;
            let mut r=Rig::new(&changed,s);r.open();r.u.edge(false);let t=r.reserve();r.publish(t,SOURCE,&payload(20,1));
        }else if mode=="burst"{
            let start=s["service_next"]-CODE;assert_eq!(&changed[start-2..start],&[6,16]);changed[start-1]=17;
            let mut r=Rig::new(&changed,s);r.u.char_cycles=100000;r.open();let t=r.reserve();r.publish(t,SOURCE,&payload(40,1));
        }else if mode=="rx"{
            let start=s["isr_dispatch"]-CODE;
            assert_eq!(&changed[start+3..start+5],&[0xcb,0x47]);
            // Replace no-pending branch with a jump to the byte-read instruction.
            let target=s["isr_rx"]-CODE;
            let pos=(target..target+40).find(|&p|changed[p..p+3]==[0xed,0x38,0xc0]).unwrap();
            changed[start+5]=0xc3;changed[start+6]=(CODE+pos)as u8;changed[start+7]=((CODE+pos)>>8)as u8;
            changed[start+8]=((CODE+pos)>>16)as u8;
            let mut r=Rig::new(&changed,s);r.open();r.irq();
        }else if mode=="release"{
            let start=s["service_more"]-CODE;
            // Change ACTIVE to RELEASED: status must expose premature release.
            let pos=(s["tx_write"]-CODE..start).find(|&p|changed[p..p+2]==[0x3e,3]).unwrap();changed[pos+1]=4;
            let mut r=Rig::new(&changed,s);r.open();r.u.cut=Some(1);let t=r.reserve();r.publish(t,SOURCE,&payload(64,1));
            let(state,n)=r.state(t);assert!(state!=4||n==64,"early source release");
        }else if mode=="txack"{
            // Remove the exit before another acknowledged IIR TX cause.
            let pos=s["isr_next"]-CODE;
            assert_eq!(changed[pos],0x3a);assert_eq!(changed[pos+5],0x20);
            changed[pos..pos+7].fill(0);
            stalls(&changed,s);
        }else if mode=="wakeup"{
            let exit=s["isr_next"]-CODE;
            changed[exit..exit+7].fill(0);
            let pos=s["isr_modem"]-CODE;
            let original=changed[pos..pos+11].to_vec();
            assert_eq!(original[0],0x3a);assert_eq!(original[5],0x20);assert_eq!(original[7],0xcd);
            // Restore the actual bug: consume DCTS before checking TX budget,
            // then skip reconciliation when this entry has already serviced TX.
            changed[pos..pos+4].copy_from_slice(&original[7..11]);
            changed[pos+4..pos+8].copy_from_slice(&original[..4]);
            changed[pos+8]=0xb7;changed[pos+9]=0x20;
            changed[pos+10]=(s["isr_next"] as isize-(CODE+pos+11)as isize)as u8;
            stalls(&changed,s);
        }else if mode=="interleave"{

            let pos=s["sync_core"]-CODE;
            // Remove drain_core call so a normal byte can cross inside payload.
            let call=(pos..pos+60).find(|&p|changed[p..p+4]==[0xcd,s["drain_core"]as u8,(s["drain_core"]>>8)as u8,(s["drain_core"]>>16)as u8]).unwrap();
            changed[call..call+4].fill(0);changed[call]=0xaf;barrier(&changed,s);
        }else{panic!("unknown negative")}
        panic!("negative control survived");
    }
}
// Execute production ROM instructions and real MOS receive parser. This does
// not boot MOS: initialized C data and peripheral startup are Flexe's job.
fn production(image:&[u8],s:&BTreeMap<String,usize>) {
    let mut cases=0;
    // Reproduce the physical fixture's attribution defect on the accepted ROM:
    // a historical latch survives entirely clean transmit/drain/close traffic.
    {
        let mut r=Rig::new(image,s);
        let latch=r.at("tx_rx_errors");r.u.mem[latch]=0x98;
        r.open();let t=r.reserve();r.publish(t,SOURCE,&payload(128,17));r.settle();
        r.call("tx_reap",t,0,0);assert_eq!(r.call("tx_close",0,0,0).0,0);
        assert_eq!(r.u.errors,0);assert_eq!(r.byte("tx_rx_errors"),0x98);
        println!("CONFIRMED stale RX 0x98 survives error-free transmission; old fixture would fail its lifetime-latch check");
        cases+=1;
    }
    if s.contains_key("tx_diag_take") {
        for iff in [false,true] { for errors in [2,4,8,16,128,0x98] {
            let mut r=Rig::new(image,s);r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
            let latch=r.at("tx_rx_errors");r.u.mem[latch]=0x98;
            let modem=r.at("tx_modem_deltas");r.u.mem[modem]=3;
            let (status,prior,_)=r.call("tx_diag_take",0,0,0);
            assert_eq!((status,prior),(0,0x398));
            assert_eq!(r.byte("tx_rx_errors"),0);assert_eq!(r.byte("tx_modem_deltas"),0);
            assert_eq!(r.call("tx_diag_take",0,0,0).1,0,"stale errors contaminated a clean epoch");
            // The same bits occurring again must still be detected; simply
            // subtracting an old bit mask would incorrectly hide these.
            r.u.errors=errors;r.u.rx.push_back(0x42);r.u.ier=0;
            assert_eq!(r.call("tx_diag_take",0,0,0).1,errors as u32);
            assert_eq!(r.u.rx.front(),Some(&0x42),"diagnostic snapshot discarded RX data");
            assert_eq!(r.byte("tx_rx_errors"),0);
            cases+=1;
        }}
        println!("PASS diagnostic epochs: stale flags separated, repeated fresh bits detected, unread RX retained, both IFF states preserved");
        let mut r=Rig::new(image,s);r.open();r.u.edge(false);let t=r.reserve();
        r.publish(t,SOURCE,&payload(64,5));
        r.cpu.registers().iff1=false;r.cpu.registers().iff2=false;
        r.u.edge(true);let delta=r.u.delta;
        assert_eq!(r.call("tx_diag_take",0,0,0).0,1);
        assert_eq!(r.u.delta,delta,"BUSY diagnostic read acknowledged a CTS wakeup");
        r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;
        r.settle();assert_eq!(r.u.wire,payload(64,5));cases+=1;
    }
    for iff in [false,true] {
        let mut r=Rig::new(image,s);r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
        r.cpu.registers().set_a(0x50);
        let (status,discover,_) = r.call("mos_api",0,0,0x1300);
        assert_eq!(status,0);assert_eq!(discover,s["uart0_async_getapi"]as u32);
        let (_,table,_) = r.call("uart0_async_getapi",0,0,0);
        assert_eq!(&r.u.mem[table as usize..table as usize+4],b"UTX1");
        assert_eq!(r.u.mem[table as usize+4],1);
        if s.contains_key("tx_diag_take") {
            assert_eq!(r.u.mem[table as usize+5],1);
            assert_eq!(r.u.mem[table as usize+6],46);
            assert_eq!(r.u.u24(table as usize+43),s["tx_diag_take"] as u32);
        }
        let ops=["tx_open","tx_reserve","tx_publish","tx_status","tx_cancel","tx_reap","tx_poll_drain","tx_close","tx_kick"];
        for (i,name) in ops.iter().enumerate(){assert_eq!(r.u.u24(table as usize+13+3*i),s[*name]as u32);}
        r.open();let t=r.reserve();
        for (p,n) in [(0,1),(0x4000,1),(0xbc000,1),(0xbbfff,2),(SOURCE as u32,0),(SOURCE as u32,65536)] {
            assert_eq!(r.call("tx_publish",t,p,n).0,2);assert_eq!(r.state(t),(1,0));
        }
        let bytes=payload(180,7);r.publish(t,SOURCE,&bytes);
        // Legacy byte with pending async work must preserve primary registers,
        // flags except documented carry, MBASE and IFF and appear at the end.
        r.cpu.registers().set_a(b'!');
        assert_eq!(r.call("UART0_serial_PUTCH",0x123456,0x654321,0x1234).0,b'!');
        assert_eq!(r.u.writes,[bytes.clone(),vec![b'!']].concat());
        assert_eq!(r.state(t),(4,180));assert_eq!(r.byte("tx_barrier"),0);
        assert_eq!(r.byte("uart0_sync_depth"),0);
// Exercise the actual ZDS C stdout wrapper and formatted MOS errors
// with pending async commands, using the native three-byte stack ABI.
for (function,arg,expected) in [("_putch",b'C' as u32,vec![b'C']), ("_mos_error",20,b"\n\rInvalid command\n\r".to_vec())] {
    let prior=payload(65,42);let ticket=r.reserve();r.publish(ticket,SOURCE+0x4000,&prior);
    let addr=SOURCE+0x5000;let target=s[function];
    let code=[0xfd,0xe5,0xdd,0xe5,0x21,arg as u8,(arg>>8)as u8,(arg>>16)as u8,0xe5,
        0xcd,target as u8,(target>>8)as u8,(target>>16)as u8,0xc1,0xdd,0xe1,0xfd,0xe1,0xc9];
    r.u.mem[addr..addr+code.len()].copy_from_slice(&code);r.s.insert("c_output".into(),addr);
    r.call("c_output",0,0,0);assert!(r.u.writes.ends_with(&[prior,expected].concat()));
    assert_eq!(r.state(ticket),(4,65));r.call("tx_reap",ticket,0,0);
}
        // Foreground polling must deliver a real GP reply even with DI.
        r.u.rx.extend([0x80,1,0x3c]);r.call("uart0_sync_begin",0,0,0);r.call("uart0_sync_end",0,0,0);
        assert_eq!(r.byte("_gp"),0x3c);
        // Callback installation fences pending bytes and closes the session.
        let pending=payload(117,9);let t2=r.reserve();r.publish(t2,SOURCE+0x1000,&pending);
        let cb=SOURCE+0x2000;let output=s["UART0_serial_PUTCH"];let open=s["tx_open"];
        let record=cb+40;
        let code=[0xcd,open as u8,(open>>8)as u8,(open>>16)as u8,
            0x32,record as u8,(record>>8)as u8,(record>>16)as u8,
            0x3e,b'K',0xcd,output as u8,(output>>8)as u8,(output>>16)as u8,0xc9];
        r.u.mem[cb..cb+code.len()].copy_from_slice(&code);
        r.cpu.registers().set_a(0x1d);r.call("mos_api",0,cb as u32,0);
        assert_eq!(r.byte("tx_opened"),0);assert_eq!(r.word("_user_kbvector"),cb as u32);
        assert_eq!(r.call("tx_open",0,0,0).0,1);
        assert!(r.u.writes.ends_with(&pending));
        // Real keyboard packet invokes a synchronous-printing callback only
        // with async closed; new API returns CONTEXT inside the ISR.
        r.u.rx.extend([0x81,4,b'x',0,65,1]);
        r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.irq();
        assert_eq!(r.u.mem[record],4);assert_eq!(r.u.writes.last(),Some(&b'K'));
        assert_eq!(r.byte("_keyascii"),b'x');assert_eq!(r.byte("_keycount"),1);
        r.cpu.registers().set_a(0x1d);r.call("mos_api",0,0,0);
        r.open();let next=r.reserve();assert!(next>t2);
        r.call("tx_cancel",next,0,0);r.call("tx_reap",next,0,0);
        r.u.advance(10000);assert_eq!(r.call("tx_close",0,0,0).0,0);
        cases+=1;
    }
for mb in [1,4,7,0x53] {
    let mut r=Rig::new(image,s);r.open();let t=r.reserve();let bytes=payload(100,3);r.publish(t,SOURCE,&bytes);
    r.cpu.registers().mbase=mb;
    assert_eq!(r.call("tx_reserve",0,0,0).0,4); // Public API rejects MBASE != 0.
    r.cpu.registers().set_a(b'M');r.call("UART0_serial_PUTCH",0,0,0);
    assert_eq!(r.u.writes,[bytes,vec![b'M']].concat());
    r.call("uart0_return_fence",0,0,0);assert_eq!(r.byte("tx_opened"),0);
    cases+=1;
}
    // A return fence cannot close, discard the queue or relinquish RAM while
    // CTS is blocked; it can finish once CTS resumes even with IFF disabled.
    for accepted in [0,1,7,16,33] {
        let mut r=Rig::new(image,s);r.open();r.u.cut=Some(accepted);
        let t=r.reserve();let bytes=payload(129,19);r.publish(t,SOURCE,&bytes);
        if accepted>16 { for _ in 0..10{r.u.advance(3000);if r.u.pending(){r.irq()}} }
        r.u.edge(false);r.u.cut=None;
        r.cpu.registers().iff1=false;r.cpu.registers().iff2=false;
        let addr=r.at("uart0_return_fence");
        r.u.mem[STUB..STUB+5].copy_from_slice(&[0xcd,addr as u8,(addr>>8)as u8,(addr>>16)as u8,0]);
        r.cpu.state.set_pc(STUB as u32);
        for _ in 0..3000 {r.step();assert_ne!(r.cpu.state.pc(),STUB as u32+4);}
        assert_eq!(r.byte("tx_opened"),1);assert_ne!(r.word("tx_head"),0);
        assert_eq!(&r.u.mem[SOURCE..SOURCE+bytes.len()],&bytes);
        r.u.edge(true);let mut steps=0;
        while r.cpu.state.pc()!=STUB as u32+4 {r.step();steps+=1;assert!(steps<100000);}
        assert_eq!(r.byte("tx_opened"),0);assert_eq!(r.byte("uart0_sync_depth"),0);
        assert_eq!(r.u.wire,bytes);assert!(r.u.shift.is_none());assert_eq!(r.word("tx_head"),0);
        assert!(!r.cpu.registers().iff1);assert!(!r.cpu.registers().iff2);
        cases+=1;
    }
for opened in [false,true] {
    let mut r=Rig::new(image,s);
    if opened{r.open();r.u.edge(false);let t=r.reserve();r.publish(t,SOURCE,&payload(70,6));}
    let at=r.at("tx_in_isr");r.u.mem[at]=1;
    r.cpu.registers().iff1=false;r.cpu.registers().iff2=false;
    let addr=r.at("_on_crash");
    r.u.mem[STUB..STUB+5].copy_from_slice(&[0xcd,addr as u8,(addr>>8)as u8,(addr>>16)as u8,0]);
    r.cpu.state.set_pc(STUB as u32);
    for _ in 0..6000{r.step();}
    if opened {
        assert!(r.cpu.state.halted);assert!(r.u.writes.is_empty());assert_eq!(r.byte("tx_opened"),1);assert_ne!(r.word("tx_head"),0);
    } else {
        assert!(r.u.writes.windows(15).any(|w|w==b"Guru meditation"));
    }
    cases+=1;
}
    println!("PASS {cases} production-ROM integration scenarios: discovery, RAM validation, ordinary output ordering, real GP/keyboard parser, callback exclusion and CTS-stalled return retention/recovery");
}

fn main(){
    let args:Vec<_>=env::args().collect();let image=fs::read(&args[1]).unwrap();
    let text=fs::read_to_string(&args[2]).unwrap();let mut symbols=BTreeMap::new();
    for l in text.lines(){let p:Vec<_>=l.split_whitespace().collect();if p.len()==3{symbols.insert(p[2].to_string(),usize::from_str_radix(p[0],16).unwrap());}}
    if symbols.contains_key("uart0_sync_depth") { production(&image,&symbols); return; }
    negative_controls(&image,&symbols);
    let mut n=0;
    for (name,test) in [("basic",basic as fn(&[u8],&BTreeMap<String,usize>)->usize),("ownership",ownership),("address-width",address_width),("stalls",stalls),("reception",reception),("barrier",barrier),("duplex",duplex),("registers",registers),("random",random_queue)]{eprintln!("Running {name}");n+=test(&image,&symbols);}
    println!("PASS {n} assembled-driver scenarios (includes 100 randomized 300-operation sequences)");
    println!("variant,masked_producer_instructions,model_cycles,isr_cycles,useful_iterations_overlapping_uart,isr_entries,wire_bytes,max_mask_model_cycles,wire_completion_model_cycles");
    let blocking=benchmark(&image,&symbols,false,0);println!("blocking,0,{},{},{},{},{},{},{}",blocking.0,blocking.1,blocking.2,blocking.3,blocking.4,blocking.5,blocking.6);
    for mask in [0,64,256,1024,4096,16384]{let b=benchmark(&image,&symbols,true,mask);println!("async,{mask},{},{},{},{},{},{},{}",b.0,b.1,b.2,b.3,b.4,b.5,b.6);}
}
