"""Independent counted-frame and report oracle; stopped host analysis only."""
import re
SIZES=[0,1,2,8,16,17,127,255,256,512,17,16,1,512,1]+[1,17]*8+[512]
def verify(data,report):
 frames=[];legacy=[];i=0;started=False;ended=False
 while i<len(data):
  tag=data[i];i+=1
  if tag<0x80:raise AssertionError(f'unframed reply byte {tag:02x} at {i-1}')
  width=2 if tag==0x90 else 1
  if i+width>len(data):raise AssertionError('truncated header')
  count=int.from_bytes(data[i:i+width],'little');i+=width
  body=data[i:i+count];i+=count
  if len(body)!=count:raise AssertionError('truncated payload')
  if tag==0x80 and body==b'\x30':
   assert not started,'duplicate fixture start fence'
   started=True;continue
  if tag==0x80 and body==b'\x34':
   assert started and not ended,'bad fixture end fence'
   ended=True;break # CLI/startup traffic is outside this qualified fixture.
  if tag==0x90:
   assert started and not ended,'counted frame outside fixture'
   assert body==bytes((n*157+7)&255 for n in range(count)),len(frames)
   frames.append(count)
  elif started and not ended:legacy.append((tag,body))
 assert started and ended,'fixture fences missing'
 assert frames==SIZES,frames
 keys=[b for t,b in legacy if t==0x81 and not b.startswith(b'VDPL')]
 assert len(keys)==2 and len(keys[0])>=4 and keys[0][3]==1 and keys[1][3]==0,keys
 match=re.search(r'RX005 RESULT callbacks=(\d+) work=(\d+) keys=1/1 regfail=0 ifffail=0',report)
 assert match and int(match[1])==30 and int(match[2])>0,report
 assert 'RX005 SUITE PASS' in report and 'SUITE FAIL' not in report,report
 assert report.count('counted ')==10 and 'RX005 KEY PASS down=1 up=1 bulk=512' in report
 return {'counted_frames':len(frames),'counted_payload_bytes':sum(frames),'callbacks':30,'genuine_key_packets':len(keys),'foreground_work':int(match[2]),'wire_bytes_through_end':i}
