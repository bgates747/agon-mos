const CALLBACK:usize=0x72000;
fn fixture(image:&[u8],s:&BTreeMap<String,usize>)->Rig{
 let mut r=Rig::new(image,s);r.open();
 // Callback deliberately clobbers primary/shadow/index registers; only RET
 // and preserved ADL/MBASE/IFF are required from the bounded app callback.
 let code=[0x01,0x11,0x11,0x11,0x11,0x22,0x22,0x22,0x21,0x33,0x33,0x33,
  0xdd,0x21,0x44,0x44,0x44,0xfd,0x21,0x55,0x55,0x55,
  0xd9,0x01,0x66,0x66,0x66,0x11,0x77,0x77,0x77,0x21,0x88,0x88,0x88,0xd9,0x08,0xaf,0x08,0xc9];
 r.u.mem[CALLBACK..CALLBACK+code.len()].copy_from_slice(&code);r
}
fn rst(r:&mut Rig,data:&[u8],delimited:bool){
 let source=0x48000;let stub=0x71000;r.u.mem[source..source+data.len()].copy_from_slice(data);
 if delimited {r.u.mem[source+data.len()]=0;assert!(!data.contains(&0));}
 let n=if delimited{0}else{data.len()as u32};assert!(n<65536);
 let code=[0x21,source as u8,(source>>8)as u8,(source>>16)as u8,
  0x01,n as u8,(n>>8)as u8,0,0xaf,0x5b,0xdf,0xc9];
 r.u.mem[stub..stub+code.len()].copy_from_slice(&code);r.s.insert("rst_trial".into(),stub);
 r.call("rst_trial",0,0,0);
 // Immediate source overwrite must not affect the queued copy.
 r.u.mem[source..source+data.len()].fill(0xEE);
}
fn config(r:&mut Rig,mode:u8,direct:bool,cb:bool)->u8 {
 r.call("tx_write_config",0x765432,if cb{CALLBACK as u32}else{0},((mode as u32)<<8)|u32::from(direct)).0
}
fn trials(image:&[u8],s:&BTreeMap<String,usize>){
 for direct in [false,true]{for iff in [false,true]{for len in [1,15,16,17,255,256,257,1024]{
  let mut r=fixture(image,s);assert_eq!(config(&mut r,0,direct,true),0);
  r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
  let data=payload(len,19);r.u.mem[SOURCE..SOURCE+len].copy_from_slice(&data);
  let (a,id,_)=r.call("tx_write_borrowed",0,SOURCE as u32,len as u32);assert_eq!(a,0);
  assert_eq!(r.call("tx_write_last",0,0,0).1,id);
  r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.settle();
  assert_eq!(r.u.wire,data);r.assert_queue();
  if direct {assert_eq!(r.callbacks.len(),1);assert_eq!(r.callbacks[0],(id,0x765432,4,false));}
  else {let(a,got,kind)=r.call("tx_completion_take",0,0,0);assert_eq!((a,got,kind),(0,id,1));assert!(r.callbacks.is_empty());assert_eq!(r.call("tx_completion_take",0,0,0).0,1);}
  assert_eq!(r.call("tx_close",0,0,0).0,0);
 }}}
 println!("PASS borrowed convenience:32 combinations, immutable bytes, callback/event exactly once, auto reap and IFF");
 for iff in [false,true]{for len in [1,15,16,17,255,256,257,511,512,768,769,4097,65535]{for cb in [false,true]{
  println!("copied case len={len} iff={iff} cb={cb}");
  let mut r=fixture(image,s);assert_eq!(config(&mut r,1,true,cb),0);
  r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;r.inject_api=true;
  let data=payload(len,29);rst(&mut r,&data,false);
  r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.settle();
  assert!(r.u.wire==data,"copied len={len} iff={iff}: lengths wire={} source={} first_difference={:?}",r.u.wire.len(),data.len(),r.u.wire.iter().zip(&data).position(|(a,b)|a!=b));r.assert_queue();
  assert_eq!(r.callbacks.len(),usize::from(cb));if cb{assert_eq!(r.callbacks[0].0,1);}
  assert_eq!(r.call("tx_write_last",0,0,0).1,1);assert_eq!(r.call("tx_close",0,0,0).0,0);
  assert_eq!(r.byte("tx_write_mode"),0);
 }}}
 println!("PASS copied RST18:52 combinations, source overwrite, >queue-size writes, DI/EI, optional callbacks");
 for n in [0,1,16,256,257,1000]{
  let mut r=fixture(image,s);assert_eq!(config(&mut r,1,true,true),0);r.inject_api=true;
  let data=vec![0x5a;n];rst(&mut r,&data,true);r.settle();
  assert_eq!(r.u.wire,data);assert_eq!(r.callbacks.len(),1);assert_eq!(r.call("tx_close",0,0,0).0,0);
 }
 println!("PASS delimiter RST18, including empty and queue-spanning calls");
 // RST18's release convention ignores BCU for its fixed count.
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,1,true,false),0);r.inject_api=true;
  let data=payload(257,5);let source=0x48000;let stub=0x71000;
  r.u.mem[source..source+data.len()].copy_from_slice(&data);
  let code=[0x21,0,0x80,4,0x01,1,1,0xab,0xaf,0x5b,0xdf,0xc9];
  r.u.mem[stub..stub+code.len()].copy_from_slice(&code);r.s.insert("rst_trial".into(),stub);
  r.call("rst_trial",0,0,0);r.settle();assert_eq!(r.u.wire,data);
 }
 println!("PASS copied RST18 ignores nonzero BCU, preserving its low16-bit count contract");
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,0,true,true),0);r.u.mem[SOURCE]=7;
  let id=r.call("tx_write_borrowed",0,SOURCE as u32,1).1;r.settle();
  assert_eq!(r.call("tx_write_borrowed",0,0x100,1).0,2);
  assert_eq!(r.call("tx_write_last",0,0,0).1,id);assert_eq!(r.callbacks.len(),1);
 }
 println!("PASS invalid borrowed source creates no completion or last-accepted ID change");
 // Many logical calls must stay ordered and each gets one ID/callback.
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,1,true,true),0);r.inject_api=true;let mut want=vec![];
  for n in 1..25{let data=payload(n*19, n as u8);rst(&mut r,&data,false);want.extend(data);}
  r.settle();assert_eq!(r.u.wire,want);assert_eq!(r.callbacks.iter().map(|v|v.0).collect::<Vec<_>>(),(1..25).collect::<Vec<_>>());
  assert_eq!(r.call("tx_close",0,0,0).0,0);
 }
 println!("PASS24 successively queued RST18 calls, exactly-once ordered logical IDs");
 // Standalone deferred-event path: completion records must not be reordered
 // when an earlier slot is reused before older completed slots are taken.
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,0,false,false),0);let mut ids=vec![];
  for _ in 0..3{r.u.mem[SOURCE]=5;ids.push(r.call("tx_write_borrowed",0,SOURCE as u32,1).1);r.settle();}
  assert_eq!(r.call("tx_completion_take",0,0,0).1,ids[0]);
  r.u.mem[SOURCE]=7;let last=r.call("tx_write_borrowed",0,SOURCE as u32,1).1;r.settle();
  for id in [ids[1],ids[2],last]{assert_eq!(r.call("tx_completion_take",0,0,0).1,id);}
 }
 println!("PASS deferred completion FIFO across descriptor reuse");
 // Invalid configurations, active mutation and original low-level API isolation.
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,1,false,true),2);
  assert_eq!(r.call("tx_write_config",0,0x30000,1).0,2);
  assert_eq!(config(&mut r,1,true,false),0);assert_eq!(r.call("tx_reserve",0,0,0).0,1);
  assert_eq!(r.call("tx_write_borrowed",0,SOURCE as u32,1).0,1);
  r.call("uart0_return_fence",0,0,0);assert_eq!(r.byte("tx_write_mode"),0);assert_eq!(r.byte("tx_opened"),0);
 }
 println!("PASS invalid mode/callback, API isolation and return cleanup");
 // Borrowed transfer stopped by CTS, normal RX parser still runs; after resume
 // bytes and callback are complete, with no callback needed from foreground.
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,0,true,true),0);r.u.edge(false);
  let data=payload(1000,3);r.u.mem[SOURCE..SOURCE+data.len()].copy_from_slice(&data);
  assert_eq!(r.call("tx_write_borrowed",0,SOURCE as u32,data.len()as u32).0,0);
  assert!(r.u.writes.is_empty());assert!(r.callbacks.is_empty());
  r.u.rx.extend([0x80,1,0x5a]);while !r.u.rx.is_empty(){r.irq();}
  assert_eq!(r.byte("_gp"),0x5a);r.u.edge(true);r.settle();assert_eq!(r.u.wire,data);assert_eq!(r.callbacks.len(),1);
 }
 println!("PASS CTS stop/resume with simultaneous real MOS GP RX parser");
 // Direct callbacks cannot re-enter the public API, including completions
 // reached synchronously from the submitter's initial service opportunity.
 {let mut r=fixture(image,s);let addr=r.at("tx_reserve");
  let code=[0xcd,addr as u8,(addr>>8)as u8,(addr>>16)as u8,0x32,0,0x30,7,0xc9];
  r.u.mem[CALLBACK..CALLBACK+code.len()].copy_from_slice(&code);
  assert_eq!(config(&mut r,0,true,true),0);r.u.mem[SOURCE]=7;
  assert_eq!(r.call("tx_write_borrowed",0,SOURCE as u32,1).0,0);r.settle();
  assert_eq!(r.u.mem[0x73000],4);assert_eq!(r.callbacks.len(),1);
 }
 println!("PASS direct callback API reentry is rejected CONTEXT");
 {let mut r=fixture(image,s);assert_eq!(config(&mut r,0,true,true),0);r.u.edge(false);
  let data=payload(500,7);r.u.mem[SOURCE..SOURCE+data.len()].copy_from_slice(&data);
  assert_eq!(r.call("tx_write_borrowed",0,SOURCE as u32,data.len()as u32).0,0);
  r.u.edge(true);assert_eq!(r.call("uart0_return_fence",0,0,0).0,0);
  assert_eq!(r.u.wire,data);assert!(r.callbacks.is_empty());assert_eq!(r.byte("tx_opened"),0);
  r.open();rst(&mut r,b"plain",false);r.settle();assert_eq!(&r.u.wire[500..],b"plain");
  assert!(r.callbacks.is_empty());assert_eq!(r.call("tx_close",0,0,0).0,0);
 }
 println!("PASS pending return drains bytes and suppresses app callbacks before stock reopen");

}

fn comparison(image:&[u8],s:&BTreeMap<String,usize>){
 for mode in 0..4{
  let mut r=fixture(image,s);r.u.mem[CALLBACK]=0xc9;r.inject_api=true;
  if mode>0 {assert_eq!(config(&mut r,u8::from(mode==3),mode!=1,mode!=1),0);}
  let data=payload(743,11);let mut ticket=0;let mut useful=0u64;
  let started=r.u.time.get();let irq0=r.isr_cycles;
  for frame in 0..30{
   if frame>0 {if mode==0 {assert_eq!(r.call("tx_reap",ticket,0,0).0,0);}else if mode==1{assert_eq!(r.call("tx_completion_take",0,0,0).0,0);}}
   if mode==0 {ticket=r.reserve();r.publish(ticket,SOURCE,&data);}
   else if mode<3 {r.u.mem[SOURCE..SOURCE+743].copy_from_slice(&data);assert_eq!(r.call("tx_write_borrowed",0,SOURCE as u32,743).0,0);}
   else {rst(&mut r,&data,false);}
   let deadline=started+(frame+1)*307200;
   while r.u.time.get()<deadline {r.u.advance(32);useful+=1;r.maybe_irq();}
  }
  r.settle();assert_eq!(r.u.wire,data.repeat(30));
  println!("MODEL paced mode={mode} useful32_units={useful} ISR_accounted_cycles={} max_ISR_steps={} callbacks={}",r.isr_cycles-irq0,r.max_isr_steps,r.callbacks.len());
 }
}
fn main(){
 let a:Vec<_>=env::args().collect();let image=fs::read(&a[1]).unwrap();let s=fs::read_to_string(&a[2]).unwrap().lines().map(|l|{let v:Vec<_>=l.split_whitespace().collect();(v[2].to_string(),usize::from_str_radix(v[0],16).unwrap())}).collect();
 trials(&image,&s);comparison(&image,&s);
}
