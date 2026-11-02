"""Validate deterministic target records and summarize matched stage/window rates."""
import argparse,collections,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('--quick',action='store_true');p.add_argument('--output',type=Path);p.add_argument('--wire',type=Path);p.add_argument('--oracle-dir',type=Path);a=p.parse_args()
text=a.report.read_text();assert 'END PASS' in text,text[-1000:]
header=dict(x.split('=',1) for x in text.splitlines()[0].split()[1:])
hz=int(header['tick_hz']);wall=int(header['wall_hz']);assert(hz,wall)==(1152000,72000)
clock=next(x for x in text.splitlines() if x.startswith('CLOCK '));c=dict(x.split('=',1) for x in clock.split()[1:]);ratio=int(c['precision_ticks'])/int(c['wall_ticks']);assert 15<ratio<17
oracle={}
for line in (Path(__file__).parent/'tests/oracle.txt').read_text().splitlines():
 balls,collide,frame,world,pixels=line.split();oracle[int(balls),int(collide),int(frame)]=(int(world,16),int(pixels,16))
groups=collections.defaultdict(list)
for line in text.splitlines():
 if line.startswith('FRAME '):
  d={k:int(v,16 if k in ('world','pixels') else 10) for k,v in (x.split('=',1) for x in line.split()[1:])};groups[d['case']].append(d)
wire=a.wire.read_bytes() if a.wire else None;cursor=0;compared=0;previous_token=None
expected_cases=12 if a.quick else 24;expected_frames=4 if a.quick else 8
assert len(groups)==expected_cases,(len(groups),expected_cases)
summary=[]
for case,rows in groups.items():
 assert len(rows)==expected_frames,(case,len(rows))
 first=rows[0];key=tuple(first[k] for k in ('balls','collide','output','mode'))
 assert rows[0]['flags']==1 and all(r['flags']==0 for r in rows[1:])
 for i,r in enumerate(rows):
  assert tuple(r[k] for k in ('balls','collide','output','mode'))==key
  assert (r['world'],r['pixels'])==oracle[r['balls'],r['collide'],i],(case,i,'determinism')
  assert r['pairs']==(r['balls']*(r['balls']-1)//2 if r['collide'] else 0)
  assert 0<r['collision']<=r['physics'] and r['draw']>0 and r['checksum']>0
  assert r['confirm']>=r['release'] and r['confirm']>=r['submit'],(case,i,'order')
  assert 0<r['bytes']<24576 and 0<r['hud_bytes']<r['bytes']
  if r['mode']==0:assert r['release']<=r['submit']
  assert not(r['flags']&1) or 0<r['drain']<=r['confirm']
  assert 1<=r['token']<=250
  if previous_token is not None:assert r['token']==previous_token%250+1
  previous_token=r['token']
  if wire is not None:
   assert a.oracle_dir,'Wire validation needs independent host-generated frames'
   stem=f"B{r['balls']}C{r['collide']}F{i}"
   if not r['output']:
    prefix=bytes([23,0,160,i&1,112,2,23,0,160,i&1,112,0,0,75])
    at=wire.find(prefix,cursor);assert at>=cursor,(case,i,'bitmap header')
    expected=(a.oracle_dir/(stem+'.bin')).read_bytes()
    assert wire[at+14:at+14+19200]==expected,(case,i,'complete UART pixel payload')
    compared+=19200
   else:
    expected=(a.oracle_dir/(stem+'.vdu')).read_bytes()
    at=wire.find(expected,cursor);assert at>=cursor,(case,i,'circle drawing commands')
    compared+=len(expected)
   token=r['token']
   end=at+r['bytes'];assert wire[end-7:end]==bytes([23,0,195,23,0,128,token]),(case,i,'flip/reply/packet extent')
   cursor=end
 measured=rows[1:];n=len(measured)-1
 delta=lambda field:(measured[-1][field]-measured[0][field])&0xffffffff
 confirmed=n*wall/delta('presented');submitted=n*wall/delta('wall_submitted')
 # Frame intervals have a 16x clock cross-check; read/confirmation boundary
 # overhead is small compared with this finite window, not zero.
 precision_span=((measured[-1]['submitted']+measured[-1]['confirm'])-(measured[0]['submitted']+measured[0]['confirm']))&0xffffffff
 wall_span=delta('presented');assert abs(precision_span/(wall_span*16)-1)<.08,(case,'timebase cross-check')
 stages={}
 for name in ('physics','collision','draw','checksum','build','submit','release','confirm'):
  values=[r[name] for r in measured];mean=statistics.mean(values)
  stages[name]=dict(mean_ticks=mean,min_ticks=min(values),max_ticks=max(values),equivalent_fps=hz/mean if mean else None)
 summary.append(dict(case=case,balls=key[0],collisions=key[1],output=['bitmap','circles'][key[2]],transport=['standard','async-events','async-callback'][key[3]],frames=len(measured),confirmed_fps=confirmed,submitted_fps=submitted,bytes_per_frame=first['bytes'],hud_bytes=first['hud_bytes'],bytes_per_second=confirmed*first['bytes'],dedicated_drain_ticks=first['drain'],stages=stages))
 assert not(first['output']==0 and confirmed>115200/19200*1.05),'Exceeds UART physical ceiling'
assert len({(s['balls'],s['collisions'],s['output'],s['transport']) for s in summary})==expected_cases
result=dict(build=header['build'],passed=True,clock_ratio=ratio,physical_qualification=False,wire_bytes_compared=compared,cases=summary,limitations=['Source-release event timestamps include foreground observation delay.','Presentation means ordered post-flip reply, not the scanout edge.','Drain measured separately; first frame excluded from pipelined FPS.','Stage wall times include interrupt preemption and overlap; do not sum them.'])
if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
for s in summary:print(f"{s['balls']:3} balls collisions={s['collisions']} {s['output']:7} {s['transport']:14} {s['confirmed_fps']:.2f} FPS {s['bytes_per_second']:.0f} B/s submit={s['stages']['submit']['mean_ticks']:.0f} ticks")
