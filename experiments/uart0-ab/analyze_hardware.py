"""Read numbered A/B reports without assuming a reliable RTC or tick frequency."""
import json,re,statistics,sys
from pathlib import Path
directory=Path(sys.argv[1]);reports=[]
for path in sorted(directory.glob('A[0-9][0-9][0-9][0-9].dat')):
    run=path.stem[1:];b=path.read_bytes()
    assert len(b)==488 and b[:8]==b'UAB1\x01\x1e\x10\0',path
    log=(directory/f'R{run}.log').read_text()
    status=re.search(rf'END run={run} (PASS|PENDING)\b',log)
    assert status and 'TEST 8 PASS' in log,path
    rows=[]
    for n in range(30):
        r=b[8+16*n:24+16*n];mode=n%10//2
        if n//10&1:mode=4-mode
        u24=lambda i:int.from_bytes(r[i:i+3],'little')
        assert r[:3]==bytes((n//10,mode,n%2)) and u24(3)>0 and r[13:]==bytes(3),(path,n)
        rows.append(dict(repeat=r[0]+1,mode=mode,phase=r[2],ticks=u24(3),work=u24(6),
                         irqs=u24(9),late_feeds=r[12],rx_errors=r[13]))
    comparisons=[]
    for phase in (0,1):
        for mode in range(5):
            group=[r for r in rows if r['phase']==phase and r['mode']==mode]
            comparisons.append(dict(mode=mode,phase=phase,
                median_ticks=statistics.median(r['ticks'] for r in group),
                tick_range=[min(r['ticks'] for r in group),max(r['ticks'] for r in group)],
                median_work_per_tick=statistics.median(r['work']/r['ticks'] for r in group),
                late_feeds=sum(r['late_feeds'] for r in group)))
    reports.append(dict(run=run,suite_status=status.group(1),installed_mos_crc32=re.search(r'MOS_ROM128K_CRC32=(\w+)',log).group(1),
                        rows=rows,summary=comparisons))
assert reports,'No complete numbered A/B reports'
print(json.dumps(dict(report_version=1,timing='Raw MOS ticks; no assumed Hz or RTC time',
    cpu_metric='Useful loop iterations per tick, not exact CPU cycles',
    receiver_scope='735 bytes checked per phase; full bulk receiver integrity not established',reports=reports),indent=2))
