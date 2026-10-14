fn set_batch(r:&mut Rig,n:u8)->u8{r.call("tx_set_cts_batch",0,0,(n as u32)<<8).0}
fn batch_api(image:&[u8],s:&BTreeMap<String,usize>)->usize{
 let mut cases=0;
 for iff in [false,true]{
  let mut r=Rig::new(image,s);r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
  assert_eq!(set_batch(&mut r,0),3);assert_eq!(r.call("tx_get_cts_batch",0,0,0).0,3);
  assert_eq!(r.call("tx_open",0,0,0).0,0);assert_eq!(r.call("tx_get_cts_batch",0,0,0).2,1);
  for n in 0..=255u8{
   let old=r.byte("tx_cts_batch");let io=r.u.io;
   let result=set_batch(&mut r,n);
   if [1,2,4,8,16].contains(&n){assert_eq!(result,0);assert_eq!(r.u.io,io+1);assert_eq!(r.call("tx_get_cts_batch",0,0,0).2,n)}
   else{assert_eq!(result,2);assert_eq!(r.byte("tx_cts_batch"),old);assert_eq!(r.u.io,io)}
   let io=r.u.io;assert_eq!(r.call("tx_get_cts_batch",0,0,0).0,0);assert_eq!(r.u.io,io);cases+=1;
  }
  let at=r.at("tx_in_isr");r.u.mem[at]=1;assert_eq!(set_batch(&mut r,0),4);assert_eq!(r.call("tx_get_cts_batch",0,0,0).0,4);r.u.mem[at]=0;
  assert_eq!(set_batch(&mut r,16),0);assert_eq!(r.call("tx_open",0,0,0).0,1);assert_eq!(r.byte("tx_cts_batch"),16);
  let t=r.reserve();assert_eq!(set_batch(&mut r,8),0,"reservation incorrectly bound policy");
  r.u.edge(false);r.publish(t,SOURCE,&payload(100,7));let io=r.u.io;
  assert_eq!(set_batch(&mut r,0),2,"INVALID must precede BUSY");assert_eq!(set_batch(&mut r,8),1);assert_eq!(set_batch(&mut r,16),1);
  assert_eq!(r.u.io,io);assert_eq!(r.call("tx_get_cts_batch",0,0,0).2,8);
  assert_eq!(r.call("tx_close",0,0,0).0,1);assert_eq!(r.byte("tx_cts_batch"),8);
  r.u.edge(true);r.cpu.registers().iff1=true;r.cpu.registers().iff2=true;r.settle();assert_eq!(set_batch(&mut r,4),0);
  r.call("tx_reap",t,0,0);r.call("tx_barrier_enter",0,0,0);let io=r.u.io;assert_eq!(set_batch(&mut r,4),1);assert_eq!(r.u.io,io);r.call("tx_barrier_leave",0,0,0);
  // RELEASED does not imply TEMT: setter must wait for the shifted byte.
  r.u.char_cycles=100000;let t=r.reserve();r.publish(t,SOURCE,&[0x42]);assert_eq!(r.state(t),(4,1));
  assert_eq!(set_batch(&mut r,2),1);r.u.mem[SOURCE]=0xaa;r.settle();assert_eq!(r.u.wire.last(),Some(&0x42));
  assert_eq!(set_batch(&mut r,2),0);r.call("tx_reap",t,0,0);assert_eq!(r.call("tx_close",0,0,0).0,0);assert_eq!(r.byte("tx_cts_batch"),1);
  assert_eq!(r.call("tx_open",0,0,0).0,0);assert_eq!(r.call("tx_get_cts_batch",0,0,0).2,1);cases+=8;
 }
 cases
}
fn batch_boundaries(image:&[u8],s:&BTreeMap<String,usize>)->usize{
 let mut cases=0;
 for n in [1,2,4,8,16]{for a in 1..=17{for b in [1,7,16,17,31]{
  let mut r=Rig::new(image,s);r.open();assert_eq!(set_batch(&mut r,n),0);r.u.char_cycles=100000;
  r.u.edge(false);let mut tickets=vec![];let mut expected=vec![];
  for (i,len) in [a,b,19].into_iter().enumerate(){let bytes=payload(len,(i*79)as u8);let t=r.reserve();r.publish(t,0x60000+i*0x1000,&bytes);expected.extend(bytes);tickets.push(t)}
  r.u.edge(true);assert_eq!(r.call("tx_kick",0,0,0).0,0);assert_eq!(r.u.writes.len(),16,"refill cap changed at descriptor boundary");
  // Reusing each released source must not alter the queued/wire copy.
  for (i,&t) in tickets.iter().enumerate(){if r.state(t).0==4{r.u.mem[0x60000+i*0x1000..0x60100+i*0x1000].fill(0xdd)}}
  r.settle();assert_eq!(r.u.wire,expected);for t in tickets{assert_eq!(r.state(t).0,4);r.call("tx_reap",t,0,0);}assert_eq!(r.call("tx_close",0,0,0).0,0);cases+=1;
 }}}
 cases
}
fn production_batch(image:&[u8],s:&BTreeMap<String,usize>)->usize{
 let mut cases=0;
 for n in [1,2,4,8,16]{for iff in [false,true]{
  let mut r=Rig::new(image,s);r.open();assert_eq!(set_batch(&mut r,n),0);
  let at=r.at("uart0_sync_depth");r.u.mem[at]=1;let io=r.u.io;assert_eq!(set_batch(&mut r,1),1);assert_eq!(r.u.io,io);r.u.mem[at]=0;
  r.cpu.registers().mbase=7;assert_eq!(set_batch(&mut r,0),4);assert_eq!(r.call("tx_get_cts_batch",0,0,0).0,4);r.cpu.registers().mbase=0;
  let t=r.reserve();let p=payload(129,42);r.publish(t,SOURCE,&p);
  r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;r.cpu.registers().set_a(b'!');
  r.call("UART0_serial_PUTCH",0,0,0);assert!(r.u.writes.ends_with(&[p.clone(),vec![b'!']].concat()));assert_eq!(r.byte("tx_cts_batch"),n);
  r.call("tx_reap",t,0,0);let t=r.reserve();r.u.edge(false);let p=payload(77,5);r.publish(t,SOURCE,&p);
  // Run the real return fence while stopped: policy and borrowed bytes persist.
  let addr=r.at("uart0_return_fence");r.u.mem[STUB..STUB+5].copy_from_slice(&[0xcd,addr as u8,(addr>>8)as u8,(addr>>16)as u8,0]);r.cpu.state.set_pc(STUB as u32);
  for _ in 0..3000{r.step();assert_ne!(r.cpu.state.pc(),STUB as u32+4)}
  assert_eq!(r.byte("tx_opened"),1);assert_eq!(r.byte("tx_cts_batch"),n);assert_eq!(&r.u.mem[SOURCE..SOURCE+p.len()],&p);
  r.u.edge(true);let mut steps=0;while r.cpu.state.pc()!=STUB as u32+4{r.step();steps+=1;assert!(steps<100000)}
  assert_eq!(r.byte("tx_opened"),0);assert_eq!(r.byte("tx_cts_batch"),1);assert!(r.u.wire.ends_with(&p));assert_eq!(r.cpu.registers().iff1,iff);cases+=1;
 }}cases
}
fn main(){
 let args:Vec<_>=env::args().collect();let image=fs::read(&args[1]).unwrap();let s:BTreeMap<String,usize>=fs::read_to_string(&args[2]).unwrap().lines().map(|l|{let p:Vec<_>=l.split_whitespace().collect();(p[2].into(),usize::from_str_radix(p[0],16).unwrap())}).collect();
 let n=env::var("UART_BATCH_SIZE").unwrap();
 if let Some(fault)=args.get(3){
  // Mutate the configured policy behind the consumer while keeping its oracle
  // fixed to one: missing intermediate CTS guards must be rejected.
  let mut changed=image.clone();
  if fault=="burst" {
   let budget=s["tx_block_budget"];
   let pattern=[0x3e,16,0x32,budget as u8,(budget>>8)as u8,(budget>>16)as u8];
   let pos=changed.windows(6).position(|w|w==pattern).unwrap();changed[pos+1]=17;
  }else if fault=="release" {
   let count=s["tx_block_count"];
   let pattern=[0x3e,3,0xdd,0x77,0,0xed,0x4b,count as u8,(count>>8)as u8,(count>>16)as u8];
   let pos=changed.windows(pattern.len()).position(|w|w==pattern).unwrap();changed[pos+1]=4;
  }else{assert_eq!(fault,"bad-guard")}
  let mut r=Rig::new(&changed,&s);r.open();let at=r.at("tx_cts_batch");r.u.mem[at]=16;
  if fault=="bad-guard"{r.u.batch_addr=0x100;r.u.mem[0x100]=1}
  r.u.char_cycles=100000;let t=r.reserve();r.publish(t,SOURCE,&payload(100,4));
  let(state,n)=r.state(t);assert!(state!=4||n==100,"early source release");panic!("negative survived")
 }
 if s.contains_key("uart0_sync_depth"){production(&image,&s);println!("PASS production batch controls {} cases",batch_api(&image,&s)+production_batch(&image,&s));return}
 let count=basic(&image,&s)+ownership(&image,&s)+address_width(&image,&s)+stalls(&image,&s)+reception(&image,&s)+barrier(&image,&s)+duplex(&image,&s)+registers(&image,&s)+random_queue(&image,&s)+batch_api(&image,&s)+batch_boundaries(&image,&s);
 println!("PASS batch={n}: {count} assembled instruction scenarios, full wire equality and CTS group/cap oracle");
}
