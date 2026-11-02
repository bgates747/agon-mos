"""Summarize hardware live samples without claiming same-scene randomized A/B."""
import argparse,collections,json,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('report',type=Path);p.add_argument('replay',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
replay=json.loads(a.replay.read_text());assert replay['passed']
scenes={};epochs={};rows=collections.defaultdict(list);clock=None
for line in a.report.read_text().splitlines():
 if line.startswith(('FRAME ','SCENE ','SCENARIO ','CLOCK ')):
  d={k:int(v,16 if k in ('world','pixels') else 10) for k,v in (x.split('=',1) for x in line.split()[1:])}
  if line.startswith('CLOCK '):clock=d
  elif line.startswith('SCENE '):scenes[d['case']]=d
  elif line.startswith('SCENARIO '):epochs[d['case']]=d
  else:rows[d['case']].append(d)
metrics=collections.defaultdict(list);ratios=[]
for case,scene in scenes.items():
 rr=rows[case];measured=[r for r in rr if not r['flags']&1]
 if len(rr)>1:
  first,last=rr[0],rr[-1]
  precision=(last['submitted']+last['confirm'])-(first['submitted']+first['confirm'])
  wall=last['presented']-first['presented'];ratio=precision/wall
  assert abs(ratio/16-1)<.001,(case,ratio);ratios.append(ratio)
 metrics[scene['balls'],scene['collide'],scene['output'],scene['mode']].append((case,measured))
out=[]
for key,cases in sorted(metrics.items()):
 case_ids=[case for case,_ in cases];samples=[r for _,rr in cases for r in rr]
 intervals=sum(epochs[c]['measured']-1 for c in case_ids)
 wall=sum((epochs[c]['last_presented']-epochs[c]['first_presented'])&0xffffffff for c in case_ids)
 fps=intervals*72000/wall
 stages={}
 for name in ('physics','collision','draw','checksum','build','submit','release','confirm'):
  vv=[r[name] for r in samples];mean=statistics.mean(vv)
  stages[name]=dict(mean_ticks=mean,mean_ms=mean/1152,min_ms=min(vv)/1152,max_ms=max(vv)/1152,equivalent_fps=1152000/mean)
 prep=[((r['submitted']-r['first'])&0xffffffff)/1152 for r in samples]
 out.append(dict(balls=key[0],collisions=key[1],output=['bitmap','circles'][key[2]],mode=key[3],transport=['standard','async-events','async-callback'][key[3]],cases=case_ids,observed_frames=sum(epochs[c]['frames'] for c in case_ids),retained_measured_frames=len(samples),confirmed_fps=fps,bytes_per_frame=samples[0]['bytes'],bytes_per_second=fps*samples[0]['bytes'],stages=stages,mean_frame_pre_submit_ms=statistics.mean(prep)))
result=dict(run=41,hardware_observations=True,frames=replay['total_frames'],retained_frames_verified=replay['retained_frames_verified'],scenarios=replay['scenarios'],clock_ratio=clock['precision_ticks']/clock['wall_ticks'],per_scenario_clock_ratio_range=[min(ratios),max(ratios)],configuration_summaries=out,comparisons_are='Interactive observations at matching ball counts/settings; moving scene states differ, not reset/matched randomized A/B.',limits=['First drain calibration frame and user-directed SD saves excluded from rates.','Stage statistics use retained raw records; rates use full scenario summaries.','Two older raw records were overwritten, not two transmitted frames lost.','Source release is not wire drain or presentation.','Local scene hashes and post-flip acknowledgements are checked, not hardware pixel-byte readback.','SD firmware files match deployment; installed firmware fingerprints are not recorded by this application.'])
a.output.write_text(json.dumps(result,indent=2)+'\n')
for r in out:
 print(f"{r['balls']:2} balls C={r['collisions']} {r['output']:7} {r['transport']:14} {r['confirmed_fps']:6.3f} FPS | physics {r['stages']['physics']['mean_ms']:7.2f} draw {r['stages']['draw']['mean_ms']:6.2f} checksum {r['stages']['checksum']['mean_ms']:6.2f} submit {r['stages']['submit']['mean_ms']:7.3f} ms")
