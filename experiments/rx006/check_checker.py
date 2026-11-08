"""Device-free log-checker controls; these are NOT application/target results."""
import json
from pathlib import Path
import subprocess
import sys

out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=False)
analyzer = Path(__file__).with_name("analyze.py").resolve()
lines = ["RX006 START build=0123456789abcdef"]
for n in (4,8,16,32,64,128,256,1024,4096,8092):
    lines.append(f"RX006 CHECK PASS bytes={n} tx_methods=2 rx_methods=2")
for n in (128,256,1024):
    for useful in (0,1):
        for repeat in (1,2,3):
            for method in (repeat & 1, (repeat & 1)^1):
                loops = 64 if n <= 256 else 16
                replies = (n+511)//512 if method else (n+7)//8
                work = 100 if useful else 0
                lines += [f"RX006 BEGIN method={method} useful={useful} bytes={n} repeat={repeat} loops={loops}",
                          f"RX006 CELL method={method} useful={useful} bytes={n} replies={replies} repeat={repeat} loops={loops} mos_counts=100 work={work} checksum=12345678"]
lines.append("RX006 SUITE PASS")
positive = "\n".join(lines)+"\n"
cases = {
    "positive": (positive, True),
    "missing-pass": (positive.replace("RX006 SUITE PASS", ""), False),
    "missing-size": (positive.replace("RX006 CHECK PASS bytes=8092 tx_methods=2 rx_methods=2\n", ""), False),
    "wrong-chunks": (positive.replace("replies=1 ", "replies=2 ", 1), False),
    "wrong-repeat": (positive.replace("repeat=1 ", "repeat=4 ", 1), False),
    "missing-begin": (positive.replace(next(x+"\n" for x in lines if x.startswith("RX006 BEGIN")), "", 1), False),
    "unexpected-work": (positive.replace("work=0 ", "work=1 ", 1), False),
    "wrong-build": (positive.replace("0123456789abcdef", "fedcba9876543210"), False),
}
results = []
for name,(body,accepted) in cases.items():
    p=out/(name+'.log');p.write_text(body)
    r=subprocess.run([sys.executable,str(analyzer),str(p),'--out',str(out/(name+'.json')),
                      '--build','0123456789abcdef'],capture_output=True,text=True,timeout=10)
    assert (r.returncode==0)==accepted,(name,r.stdout,r.stderr)
    results.append(dict(case=name,accepted=r.returncode==0,expected=accepted))
(out/'result.json').write_text(json.dumps(dict(kind='Manufactured device-free checker controls; no target execution',results=results),indent=2)+'\n')
print(json.dumps(results,indent=2))
