"""Read-only analysis of interactive returns; keep partial/configuration windows separate."""
import argparse,collections,json,statistics,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('--oracle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
lines=a.report.read_text().splitlines();assert lines[-1].startswith('END PASS ')
header=dict(x.split('=',1) for x in lines[0].split()[1:]);hz=int(header['tick_hz']);wall=int(header['wall_hz']);assert (hz,wall)==(1152000,72000)
clock=dict(x.split('=',1) for x in next(l for l in lines if l.startswith('CLOCK ')).split()[1:]);ratio=int(clock['precision_ticks'])/int(clock['wall_ticks']);assert 15<ratio<17
rows=[];groups=collections.defaultdict(list)
for l in lines:
 if l.startswith('META '):assert 'key_overruns=0' in l,l
 if l.startswith('FRAME '):
  r={k:int(v,16 if k in ('world','pixels') else 10) for k,v in (x.split('=',1) for x in l.split()[1:])};rows.append(r);groups[r['case']].append(r)
assert len(groups)==int(lines[-1].split('case_count=')[1].split()[0])
reference={};reverse={}
for balls,collide in {(r['balls'],r['collide']) for r in rows}:
 raw=subprocess.check_output([str(a.oracle.resolve()),str(balls),str(collide),str(len(rows)+1)],text=True)
 ref={}
 for line in raw.splitlines():
  step,world,pixels,pairs,contacts=line.split();ref[int(step)]=dict(world=int(world,16),pixels=int(pixels,16),pairs=int(pairs),contacts=int(contacts))
 reference[balls,collide]=ref;reverse[balls,collide]={(r['world'],r['pixels']):step for step,r in ref.items()}
last_token=None;last_case=None;summary=[]
for case,rr in groups.items():
 first=rr[0];config=tuple(first[k] for k in ('balls','collide','output','mode'))
 start=reverse[config[:2]][first['world'],first['pixels']]
 assert 1<=len(rr)<=12 and rr[0]['flags']==1 and all(r['flags']==0 for r in rr[1:])
 for i,r in enumerate(rr):
  assert tuple(r[k] for k in ('balls','collide','output','mode'))==config
  expected=reference[config[:2]][start+i]
  assert all(r[k]==v for k,v in expected.items()),(case,i,'physics/raster mismatch')
  r['scene_step']=start+i
  assert 0<r['collision']<=r['physics'] and r['draw']>0 and r['checksum']>0
  assert r['confirm']>=r['release'] and r['confirm']>=r['submit']
  assert 1<=r['token']<=250
  if last_token is not None:
   allowed={last_token%250+1}
   # A key change can discard one already-prepared, never-submitted frame.
   if case!=last_case:allowed.add((last_token+1)%250+1)
   assert r['token'] in allowed,(case,i,'confirmation sequence')
  last_token=r['token'];last_case=case
  if r['mode']==0:assert r['release']<=r['submit']
  if i==0:assert 0<r['drain']<=r['confirm']
 measured=rr[1:];intervals=max(0,len(measured)-1)
 span=measured[-1]['presented']-measured[0]['presented'] if intervals else 0
 if intervals:
  precision=(measured[-1]['submitted']+measured[-1]['confirm'])-(measured[0]['submitted']+measured[0]['confirm'])
  assert abs(precision/(span*16)-1)<.001,(case,'clock consistency')
 summary.append(dict(case=case,balls=config[0],collisions=config[1],output=config[2],mode=config[3],first_scene_step=start,frames=len(rr),complete_block=len(rr)==12,intervals=intervals,wall_ticks=span,confirmed_fps=intervals*wall/span if span else None))
# Compare identical complete12-frame blocks starting from the same scene steps.
matched=[]
for balls,collide,output in sorted({(r['balls'],r['collide'],r['output']) for r in rows}):
 by_mode={mode:{s['first_scene_step']:s for s in summary if (s['balls'],s['collisions'],s['output'],s['mode'])==(balls,collide,output,mode) and s['complete_block']} for mode in range(3)}
 common=set.intersection(*(set(v) for v in by_mode.values()))
 if not common:continue
 modes=[]
 for mode in range(3):
  cases=[by_mode[mode][step]['case'] for step in sorted(common)]
  selected=[r for r in rows if r['case'] in cases and not r['flags']&1]
  intervals=sum(by_mode[mode][s]['intervals'] for s in common);elapsed=sum(by_mode[mode][s]['wall_ticks'] for s in common)
  stages={}
  for name in ('physics','collision','draw','checksum','build','submit','release','confirm'):
   values=[r[name] for r in selected];mean=statistics.mean(values)
   stages[name]=dict(mean_ticks=mean,mean_ms=mean*1000/hz,min_ticks=min(values),max_ticks=max(values))
  modes.append(dict(mode=mode,blocks=len(common),cases=cases,matched_frames=len(common)*12,confirmed_fps=intervals*wall/elapsed,stages=stages,bytes_per_frame=selected[0]['bytes']))
 for m in modes:m['gain_vs_standard_percent']=(m['confirmed_fps']/modes[0]['confirmed_fps']-1)*100
 matched.append(dict(balls=balls,collisions=collide,output=output,scene_block_starts=sorted(common),modes=modes))
result=dict(report=header['run'],build=header['build'],hardware_report=True,completed=True,frames=len(rows),blocks=len(groups),reference_frame_hashes_verified=len(rows),zero_reported_key_overruns=True,clock_ratio=ratio,blocks_summary=summary,matched=matched,limits=['Interactive run, not automated matrix or randomized repeated A/B.','Within-block rates exclude SD pauses, first calibration frame and partial blocks.','Local scene hashes verified; no physical UART-byte readback capture in this fixture.','Matching firmware files on SD do not identify the installed ROM or VDP image.','Direct callback posting cost alone is not total UART CPU cost.'])
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('frames','blocks','reference_frame_hashes_verified','clock_ratio')},indent=2))
for group in matched:
 print('balls',group['balls'],'collisions',group['collisions'],'output',group['output'])
 for m in group['modes']:print('mode',m['mode'],'FPS',round(m['confirmed_fps'],4),'gain%',round(m['gain_vs_standard_percent'],2),'matchedframes',m['matched_frames'],'submitms',round(m['stages']['submit']['mean_ms'],4))
