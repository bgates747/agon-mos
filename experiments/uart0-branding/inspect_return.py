"""Validate the unbranded Console8 replay; never reattribute it to a new ROM."""
import hashlib
import importlib.util
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
capture = Path(sys.argv[1]).resolve(strict=True)
h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
record = json.loads((capture / 'capture.json').read_text())
assert record['package_verified'] and record['prior_reports_preserved']
assert record['running_log_append_only'] and not record['SD_writes']
assert record['card_uuid'] == '8658-1C23'
for name, pin in record['files'].items():
    assert h(capture / name) == pin, name
assert h(capture / 'manifest.json') == 'a16101e21189c0e88467a6cd95ad636c308daab1af85cad516af10ba9de94b83'
index = (capture / 'runs.log').read_text()
def journal(run):
    text = (capture / f'R{run:04d}.log').read_text()
    assert text in index
    assert 'MOS_ROM128K_CRC32=239097B7 API=1.1' in text
    assert f'END run={run:04d} PASS' in text
    assert not re.search(r'^TEST .* (FAIL|SKIP|PENDING)$', text, re.M)
    return text

decoded = json.loads(subprocess.check_output(
    [sys.executable, str(root / 'experiments/uart0-ab/analyze_hardware.py'), str(capture)], text=True))
reports = [r for r in decoded['reports'] if int(r['run']) in (26, 27, 28)]
assert len(reports) == 3
allrows = []
for report in reports:
    run = int(report['run']); text = journal(run)
    assert 'TEST 8 PASS' in text and not (capture / f'X{run:04d}.dat').exists()
    for r in report['rows']:
        assert not r['late_feeds'] and not r['rx_errors']
        token = f"AB repeat={r['repeat']} mode={r['mode']} phase={r['phase']} ticks={r['ticks']} work={r['work']} irq={r['irqs']} late=0 rx=00"
        assert token in text
    allrows += report['rows']
text = journal(29)
assert re.findall(r'^TEST (\d+) PASS$', text, re.M) == ['1', '6', '2', '3', '10', '15']
assert 'VDP=RX-sync-candidate' in text
diag = (capture / 'D0029.dat').read_bytes()
assert len(diag) == 12 and all(diag[n] == 0 for n in (2, 3, 5, 6, 8, 9, 11))
integration = (capture / 'I0029.dat').read_bytes()
u24 = lambda b, n: int.from_bytes(b[n:n+3], 'little')
assert len(integration) == 21 and integration[:9] == b'UART0MOS\0'
assert [u24(integration, n) for n in (9, 12, 15)] == [128, 4110, 128]
assert integration[18] == 0 and integration[20] == 63
for prefix in ('N', 'P'):
    data = (capture / f'{prefix}0029.dat').read_bytes()
    assert len(data) == 3 and data[0] == 0
for prefix, size, magic, stride, count in (
    ('B', 148, b'UART0BN1\x01\0\x08\0', 17, 8),
    ('S', 76, b'UART0ST1\x01\0\x04\0', 16, 4)):
    data = (capture / f'{prefix}0029.dat').read_bytes()
    assert len(data) == size and data[:12] == magic
    assert f'REPORT {prefix}0029.dat hex={data.hex().upper()}' in text
    expected = json.loads((capture / ('bench.json' if prefix == 'B' else 'stress.json')).read_text())
    for n in range(count):
        r = data[12+n*stride:12+(n+1)*stride]
        if prefix == 'B':
            assert r[0] == ((n//2)^(n%2))%2 and r[1] == n//2
            assert u24(r,5) == expected['work_checksum'] and u24(r,11) == expected['packet_bytes']
            assert r[14] == r[16] == 0
            assert 1 <= u24(r,8) <= expected['work_iterations'] if r[0] else u24(r,8) == 0
        else:
            assert r[0] == expected['pause_frames'][n] and r[1] == r[2] == 32
            assert 1 <= r[3] <= 32 and u24(r,4) == expected['packet_bytes'][n]
            assert r[10] == r[12] == r[14] == r[15] == 0 and r[13] == 47
spec = importlib.util.spec_from_file_location('recovery', root / 'experiments/uart0-recovery/analyze.py')
recovery = importlib.util.module_from_spec(spec); spec.loader.exec_module(recovery)
data = (capture / 'Y0029.dat').read_bytes()
assert data == (capture / 'Z0029.dat').read_bytes()
receiver = recovery.analyze(data)
assert receiver['campaign_passed'] and receiver['state']['completed'] == 6
for prefix in ('C', 'F', 'G', 'J', 'K'):
    assert not (capture / f'{prefix}0029.dat').exists()
summary = []
for mode in range(5):
    paced = [r for r in allrows if r['mode'] == mode and r['phase'] == 1]
    bulk = [r for r in allrows if r['mode'] == mode and r['phase'] == 0]
    summary.append(dict(mode=mode, paced_median_useful_work=statistics.median(r['work'] for r in paced),
                        paced_work_range=[min(r['work'] for r in paced), max(r['work'] for r in paced)],
                        bulk_median_ticks=statistics.median(r['ticks'] for r in bulk)))
result = dict(physical_test_performed=True, installed_mos_crc32='239097B7', ABI='1.1',
              branded_MOS_physically_tested=False, branding_invalidates_prior_sender_results=False,
              ab_runs=[26,27,28], ab_phases_passed=90, late_feeds=0, case_RX_errors=0,
              compatibility_run=29, compatibility_passed=True, compatibility_tests=[1,6,2,3,10],
              receiver_final_buffer_bytes_verified=receiver['final_buffer_bytes_checked'],
              summary=summary, otirx_paced_work_gain_over_per_byte_percent=round(
                  (summary[4]['paced_median_useful_work']/summary[1]['paced_median_useful_work']-1)*100,2),
              full_AB_bulk_receiver_integrity_verified=False, exact_CPU_cycles_measured=False,
              VDP_identity='Candidate compatibility protocol gate; A/B same-session attribution, no independent flash readback',
              stock_VDP_restoration_confirmed=record['stock_VDP_restoration_confirmed'],
              release_qualified=False, SD_writes=False)
(capture / 'analysis.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
