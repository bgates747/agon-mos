// Dedicated experiments; rates/cycles below are model results, not silicon timing.
const HZ:i64=18_432_000;
const PERIOD:i64=HZ/60;
fn ab_symbols(path:&str)->BTreeMap<String,usize>{
 fs::read_to_string(path).unwrap().lines().map(|l|{let p:Vec<_>=l.split_whitespace().collect();(p[2].to_string(),usize::from_str_radix(p[0],16).unwrap())}).collect()
}
fn ab_packet(seed:usize)->Vec<u8>{
 let mut p=vec![23,0,0xa0,0x10,0x70,0,0xdf,2];
 p.extend((0..735).map(|i|((i*157+seed*13+7)&255)as u8));p
}
fn ab_work(r:&mut Rig,until:i64,done:&mut usize){
 r.cpu.state.halted=false;let pc=r.cpu.state.pc();let at=r.at("ab_work_tick")as u32;
 if pc!=at && pc!=at+1{r.cpu.state.set_pc(at)}
 while r.u.time.get()<until{
  if r.cpu.state.pc()==r.at("ab_work_tick")as u32{*done+=1}
  r.step();r.maybe_irq();
 }
}
fn ab_cpu(r:&Rig)->i64{r.u.cpu_cycles.get()+r.isr_count as i64*8}
fn ab_case(image:&[u8],s:&BTreeMap<String,usize>,mode:&str,kind:&str,rep:usize,fault:&str){
 let mut r=Rig::new(image,s);r.open();let start=r.u.time.get();let cpu0=ab_cpu(&r);
 let mut service=0;let mut useful=0;let mut expected=vec![];let mut tickets=vec![];
 let mut late=0;let mut max_late=0;
 if fault=="no-progress"{r.u.edge(false)}
 if kind=="bulk"{
  for n in 0..3{
   let mut p=vec![23,0,0xa0,0x10,0x70,2,23,0,0xa0,0x10,0x70,0,0xf2,0x3f];
   p.extend((0..16370).map(|i|((i*157+n*13+7)&255)as u8));let addr=0x60000+n*0x10000;
   expected.extend(&p);let before=ab_cpu(&r);
   if mode=="blocking"{r.u.mem[addr..addr+p.len()].copy_from_slice(&p);assert_eq!(r.call("blocking_send",0,addr as u32,p.len()as u32).0,0)}
   else{let t=r.reserve();r.publish(t,addr,&p);tickets.push(t)}
   service+=ab_cpu(&r)-before;
  }
  let deadline=start+HZ*3;
  while r.u.wire.len()<expected.len() && r.u.time.get()<deadline{{let end=r_work_end(&r);ab_work(&mut r,end,&mut useful)}}
  assert_eq!(r.u.wire.len(),expected.len(),"bulk transport timeout");
 }else{
  for n in 0..120{
   let due=start+n as i64*PERIOD;
   ab_work(&mut r,due,&mut useful);
   let behind=r.u.time.get()-due;if behind>128{late+=1;max_late=max_late.max(behind)}
   let before=ab_cpu(&r);
   for t in tickets.drain(..){assert_eq!(r.state(t).0,4,"source not released by next feed");assert_eq!(r.call("tx_reap",t,0,0).0,0)}
   let p=ab_packet(n);expected.extend(&p);let addr=0x60000;
   if mode=="blocking"{r.u.mem[addr..addr+p.len()].copy_from_slice(&p);assert_eq!(r.call("blocking_send",0,addr as u32,p.len()as u32).0,0)}
   else{let t=r.reserve();r.publish(t,addr,&p);tickets.push(t)}
   service+=ab_cpu(&r)-before;
  }
  ab_work(&mut r,start+120*PERIOD,&mut useful);
  assert_eq!(r.u.wire.len(),expected.len(),"paced feed missed final window");
 }
 if fault=="corrupt"{r.u.wire[17]^=1}
 assert!(r.u.wire==expected,"payload byte corruption");
 assert_eq!(r.word("tx_head"),0);
 let elapsed=r.u.time.get()-start;let wire_elapsed=r.u.wire_done-start;
 let cost=service+r.isr_cycles; // API instructions plus complete modeled IRQ entry/service.
 for t in tickets{assert_eq!(r.state(t).0,4);assert_eq!(r.call("tx_reap",t,0,0).0,0)}
 assert_eq!(r.call("tx_close",0,0,0).0,0);assert_eq!(r.u.ier,1);
 println!("{rep},{kind},{mode},{},{elapsed},{wire_elapsed},{cost},{useful},{},{},{late},{max_late},{}",expected.len(),r.isr_count,r.u.cts_reads,r.u.max_fifo);
 assert!(ab_cpu(&r)>=cpu0);
}
fn r_work_end(r:&Rig)->i64{r.u.time.get()+64}
fn ab_stalls(image:&[u8],s:&BTreeMap<String,usize>){
 for cut in 0..35{
  let mut r=Rig::new(image,s);r.open();r.u.cut=Some(cut);let p:Vec<_>=(0..71).map(|i|i as u8).collect();let t=r.reserve();r.publish(t,0x60000,&p);
  for _ in 0..64{r.u.advance(160);r.maybe_irq()}
  assert!(r.u.writes.len()<=cut+16,"unbounded CTS overshoot");
  let stopped=r.u.writes.len();for _ in 0..8{r.u.advance(160);r.maybe_irq()}
  assert_eq!(r.u.writes.len(),stopped,"writing without CTS recovery");
  r.u.cut=None;r.u.edge(true);r.settle();assert_eq!(r.u.wire,p);
  assert_eq!(r.state(t),(4,71));assert_eq!(r.call("tx_reap",t,0,0).0,0);assert_eq!(r.call("tx_close",0,0,0).0,0);
 }
}
fn main(){
 let args:Vec<_>=env::args().collect();let root=&args[1];let fault=args.get(2).map(String::as_str).unwrap_or("");
 let names=["blocking","default","grouped","chunk","otirx"];
 println!("repeat,workload,mode,wire_bytes,elapsed_model_cycles,wire_completion_model_cycles,service_model_cycles,useful_iterations,isr_entries,cts_reads,late_feeds_over_128_cycles,max_late_model_cycles,max_fifo");
 for rep in 0..3{
  for i in 0..names.len(){let mode=names[if rep%2==0{i}else{names.len()-1-i}];let kernel=if mode=="blocking"{"default"}else{mode};
   let image=fs::read(format!("{root}/{kernel}/driver.bin")).unwrap();let s=ab_symbols(&format!("{root}/{kernel}/symbols.txt"));
   if rep==0{
 ab_stalls(&image,&s);
 let checks=basic(&image,&s)+ownership(&image,&s)+address_width(&image,&s)+reception(&image,&s)+barrier(&image,&s)+duplex(&image,&s)+registers(&image,&s)+random_queue(&image,&s);
 eprintln!("PASS {kernel}: {checks} inherited contract scenarios plus 35 bounded CTS cut/resume cases");
}
   for kind in ["bulk","paced"]{ab_case(&image,&s,mode,kind,rep,fault)}
  }
 }
}
