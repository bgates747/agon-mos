"""Offline target-only probe review. Retain malformed frames without forced indexing."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
root=Path(sys.argv[1]).resolve(strict=True)
meta=json.loads((root/'result.json').read_text())
assert meta['probe_setup'] in ('target-only','target-plus-red')
rate=24000000;offsets=[-120,-24,0,24,120];tx_clocks=list(range(9))+[17,26,35,44]
reports=[]
for phase in meta['phases']:
 path=root/(phase['id']+'.bin');data=np.memmap(path,dtype=np.uint8,mode='r');assert len(data)==96000000
 delta=data[1:]^data[:-1]
 rises=np.flatnonzero((delta&1)&(data[1:]&1))+1
 falls=np.flatnonzero((delta&1)&((data[1:]&1)==0))+1
 frames=np.split(rises,np.flatnonzero(np.diff(rises)>24000)+1)
 assert len(frames)==len(phase['readings'])==5
 report=dict(capture=path.name,sha256=hashlib.sha256(data).hexdigest(),clock_rises=len(rises),clock_falls=len(falls),
  channel_edge_counts={f'D{c}':int(np.count_nonzero(delta&(1<<c))) for c in range(8)},frames=[])
 for index,(frame,reading) in enumerate(zip(frames,phase['readings']),1):
  row=dict(trial=index,raw_clock_rises=len(frame),cpu_reply=reading['raw'],cpu_valid=reading['valid'],mapping_valid=len(frame)==45)
  if len(frame)==45:
   row['target_tx_correct_by_offset']={str(o):sum(int((data[int(frame[c])+o]>>2)&1)==t['desired'] for c,t in zip(tx_clocks,reading['tx'])) for o in offsets}
   row['target_reply_by_offset']={}
   for o in offsets:
    bits=(data[frame+o]>>2)&1
    values=[sum(int(v)<<(7-i) for i,v in enumerate(bits[start:start+8])) for start in [9,18,27,36]]
    row['target_reply_by_offset'][str(o)]=' '.join(f'{v:02X}' for v in values)
   row['all_reply_offsets_match_cpu']=all(v==reading['raw'] for v in row['target_reply_by_offset'].values())
  report['frames'].append(row)
 reports.append(report)
result=dict(scope='Offline target-end analysis; no WROOM-side analyzer probes attached',sample_rate_hz=rate,probe_map=meta['probe_map'],phases=reports,
 limits=['Logic thresholds only; no analog voltage/current measurement','Malformed clock counts are retained; TX/reply decoding is omitted for such frames','Offsets are samples: -120=-5us, -24=-1us, +24=+1us, +120=+5us','WROOM local GPIO trace is not a simultaneous WROOM-side analyzer trace'])
p=root/'target-probe-review.json'
with p.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
