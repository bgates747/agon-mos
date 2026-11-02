"""Validate v2 live reports, including preserved scenes and raw-ring rollover."""
import argparse,collections,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('--oracle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--require-rollover',action='store_true');p.add_argument('--hardware-report',action='store_true',help='Author identifies the report as hardware; does not imply full-matrix qualification');a=p.parse_args()
lines=a.report.read_text().splitlines();assert lines[-1].startswith('END PASS ')
def fields(l):return {k:int(v,16 if k in ('world','pixels') else 10) for k,v in (x.split('=',1) for x in l.split()[1:])}
scenes={};summaries={};groups=collections.defaultdict(list)
for line in lines:
 if line.startswith('SCENE '):d=fields(line);scenes[d['case']]=d
 if line.startswith('SCENARIO '):d=fields(line);summaries[d['case']]=d
 if line.startswith('FRAME '):d=fields(line);groups[d['case']].append(d)
 if line.startswith('META '):assert 'key_overruns=0' in line
assert set(scenes)==set(summaries)==set(groups)
commands=''.join(f"{case} {s['balls']} {s['collide']} {s['fresh']} {summaries[case]['frames']}\n" for case,s in scenes.items())
raw=subprocess.check_output([str(a.oracle.resolve())],input=commands,text=True)
reference={}
for line in raw.splitlines():
 case,frame,step,world,pixels,pairs,contacts=line.split();reference[int(case),int(frame)]=dict(step=int(step),world=int(world,16),pixels=int(pixels,16),pairs=int(pairs),contacts=int(contacts))
previous_scene=None;token_seed=None;total=retained=overwritten=0;out=[]
for case,scene in scenes.items():
 summary=summaries[case];rows=groups[case];n=summary['frames'];keep=min(128,n)
 assert summary['retained']==len(rows)==keep
 assert summary['overwritten']==n-keep
 assert [r['frame'] for r in rows]==list(range(n-keep+1,n+1))
 for r in rows:
  if token_seed is None:token_seed=(r['token']-1-(total+r['frame']-1))%250
  assert r['token']==(token_seed+total+r['frame']-1)%250+1
  assert all(r[k]==v for k,v in reference[case,r['frame']].items()),(case,r['frame'],'replay')
  assert tuple(r[k] for k in ('mode','output','balls','collide'))==tuple(scene[k] for k in ('mode','output','balls','collide'))
  assert bool(r['flags']&1)==(r['frame']==1)
  assert r['confirm']>=r['submit'] and r['confirm']>=r['release']
  assert 0<r['collision']<=r['physics']
 if previous_scene is not None:
  previous_case=previous_scene['case'];expected=0 if scene['fresh'] else scenes[previous_case]['start_step']+summaries[previous_case]['frames']
  assert scene['start_step']==expected,(case,'automatic scene restart')
 previous_scene=scene;total+=n;retained+=keep;overwritten+=n-keep
 fps=((summary['measured']-1)*72000/((summary['last_presented']-summary['first_presented'])&0xffffffff)) if summary['measured']>1 else None
 out.append(dict(case=case,mode=scene['mode'],output=scene['output'],balls=scene['balls'],collisions=scene['collide'],fresh=scene['fresh'],frames=n,retained=keep,overwritten=n-keep,scenario_fps=fps))
if a.require_rollover:assert overwritten>0,'No long-running scenario exercised the ring'
result=dict(passed=True,total_frames=total,retained_frames_verified=retained,overwritten_raw_frames=overwritten,scenarios=len(scenes),scene_continuity_verified=True,cases=out,hardware_report=a.hardware_report,full_hardware_matrix_qualified=False)
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
