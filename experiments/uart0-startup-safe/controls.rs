fn startup_controls(image:&[u8],s:&BTreeMap<String,usize>){
 // Invoke RST.LIL 18 itself, not just the UART functions it eventually calls.
 // The release body returns with RET.L and needs a mixed-mode call frame.
 for active in [false,true]{for iff in [false,true]{for delimited in [false,true]{
  let mut r=Rig::new(image,s);if active{r.open();}
  r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
  let payload=SOURCE+0x7000;r.u.mem[payload..payload+4].copy_from_slice(b"RST\0");
  let stub=SOURCE+0x7100;
  let count=if delimited{0}else{3};
  let code=[0x21,payload as u8,(payload>>8)as u8,(payload>>16)as u8,
            0x01,count,0,0,0xaf,0x5b,0xdf,0xc9];
  r.u.mem[stub..stub+code.len()].copy_from_slice(&code);r.s.insert("rst_output".into(),stub);
  r.call("rst_output",0,0,0);r.settle();
  assert_eq!(r.u.wire,b"RST");assert_eq!(r.cpu.registers().iff1,iff);
  assert_eq!(r.byte("uart0_sync_depth"),0);
 }} }
 println!("PASS actual mixed-mode RST18 output/return, fixed/delimited, stock/active, both IFF states");
 for iff in [false,true]{
  let mut r=Rig::new(image,s);r.cpu.registers().iff1=iff;r.cpu.registers().iff2=iff;
  let vector=r.at("__2nd_jump_table")+0x31;
  let stock=s["_uart0_handler"]as u32;
  assert_eq!(r.byte("tx_opened"),0);assert_eq!(r.byte("uart0_initialized"),0);
  assert_eq!(r.u.u24(vector),stock);
  r.call("uart0_async_getapi",0,0,0);
  assert_eq!(r.byte("uart0_initialized"),0,"discovery activated transport");
  // A caller-owned IRQ vector must survive a rejected activation.
  r.u.set24(vector,0x50000);assert_eq!(r.call("tx_open",0,0,0).0,1);
  assert_eq!(r.u.u24(vector),0x50000);assert_eq!(r.byte("uart0_initialized"),0);
  r.u.set24(vector,stock);
  r.open();assert_eq!(r.u.u24(vector),s["tx_isr"]as u32);
  assert_eq!(r.byte("uart0_initialized"),1);assert_eq!(r.word("tx_next_ticket"),1);
  let t=r.reserve();r.call("tx_cancel",t,0,0);r.call("tx_reap",t,0,0);
  assert_eq!(r.call("tx_close",0,0,0).0,0);assert_eq!(r.u.u24(vector),stock);
  assert_eq!(r.byte("tx_opened"),0);r.open();assert_eq!(r.word("tx_next_ticket"),2);
  r.call("uart0_return_fence",0,0,0);assert_eq!(r.u.u24(vector),stock);
  assert_eq!(r.byte("tx_opened"),0);assert_eq!(r.cpu.registers().iff1,iff);
 }
 println!("PASS stock discovery, explicit vector takeover/refusal, lazy state, close/reopen and return restoration in both IFF states");
}
