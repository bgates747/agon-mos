"""Check complete RX006 returned log coverage; summarize matched coarse timings."""
import argparse
import json
from pathlib import Path
import re

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("log", type=Path)
p.add_argument("--out", type=Path, required=True)
p.add_argument("--build", help="Require exact current fixture build identity")
a = p.parse_args()
text = a.log.read_text()
starts = re.findall(r"^RX006 START build=([0-9a-f]{16})$", text, re.M)
assert len(starts) == 1 and text.count("RX006 SUITE PASS") == 1
assert not a.build or starts == [a.build]
checks = list(map(int, re.findall(r"^RX006 CHECK PASS bytes=(\d+) tx_methods=2 rx_methods=2$", text, re.M)))
assert checks == [4,8,16,32,64,128,256,1024,4096,8092]
pattern = (r"^RX006 CELL method=(\d+) useful=(\d+) bytes=(\d+) replies=(\d+) "
           r"repeat=(\d+) loops=(\d+) mos_counts=(\d+) work=(\d+) checksum=([0-9A-Fa-f]{8})$")
cells = []
for m in re.finditer(pattern, text, re.M):
    method, useful, size, replies, repeat, loops, ticks, work = map(int, m.groups()[:8])
    assert method in (0,1) and useful in (0,1) and size in (128,256,1024)
    assert repeat in (1,2,3) and loops == (64 if size <= 256 else 16)
    assert replies == (size + (511 if method else 7)) // (512 if method else 8)
    assert useful or work == 0
    cells.append(dict(method=method, useful=useful, size=size, replies=replies,
                      repeat=repeat, loops=loops, mos_counts=ticks, work=work,
                      checksum=m.group(9)))
expected = [(n,u,r,first) for n in (128,256,1024) for u in (0,1)
            for r in (1,2,3) for first in (r & 1, (r & 1)^1)]
assert [(c['size'],c['useful'],c['repeat'],c['method']) for c in cells] == expected
begins = [tuple(map(int,m)) for m in re.findall(
    r"^RX006 BEGIN method=(\d+) useful=(\d+) bytes=(\d+) repeat=(\d+) loops=(\d+)$", text, re.M)]
assert begins == [(x['method'],x['useful'],x['size'],x['repeat'],x['loops']) for x in cells]
comparisons = []
for n in (128,256,1024):
    for useful in (0,1):
        pair = []
        for method in (0,1):
            rows = [x for x in cells if (x['size'],x['useful'],x['method']) == (n,useful,method)]
            pair.append(dict(method=method, batch_payload_bytes=sum(x['size']*x['loops'] for x in rows),
                             requests=sum(x['replies']*x['loops'] for x in rows),
                             mos_counts=sum(x['mos_counts'] for x in rows),
                             work=sum(x['work'] for x in rows)))
        assert pair[0]['batch_payload_bytes'] == pair[1]['batch_payload_bytes']
        old, new = pair
        comparisons.append(dict(size=n,useful=useful,legacy=old,counted=new,
                                coarse_completion_ratio=old['mos_counts']/new['mos_counts'] if new['mos_counts'] else None,
                                low_resolution=any(x['mos_counts'] < 20 for x in pair)))
result = dict(build=starts[0], correctness_sizes=checks, cells=cells, comparisons=comparisons,
              qualification="Returned application byte-oracle/callback/count/guard pass; public MOS-count batches, not calibrated CPU or pure wire rate. Zero/short times are unresolved.")
a.out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(dict(build=starts[0],checks=len(checks),cells=len(cells),comparisons=comparisons),indent=2))
