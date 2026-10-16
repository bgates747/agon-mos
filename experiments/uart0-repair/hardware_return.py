"""Validate an archived Console8 before/after return without accessing the SD."""
import argparse
import hashlib
import importlib.util
import json
import re
import zlib
from pathlib import Path

from analyze import analyze


def inspect(capture, baseline_run, fixed_run, candidate_run, restore_run):
    root = Path(__file__).resolve().parents[2]
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    record = json.loads((capture / 'capture.json').read_text())
    assert record['package_verified'] and record['prior_reports_preserved']
    assert record['running_log_append_only'] and not record['SD_writes']
    assert record['mount']['uuid'].upper() == '8658-1C23'
    assert record['mount']['label'] == 'AGONC8'
    for name, pin in record['files'].items():
        assert Path(name).name == name and digest(capture / name) == pin, name
    assert digest(capture / 'manifest.json') == '7254147bd00d48806ba78560e9c7b5a20fd101f732fd51e201c73d46ff8eebed'
    manifest = json.loads((capture / 'manifest.json').read_text())
    assert manifest['target'] == 'Heber Agon Console8' and manifest['receiver_sync_repair']
    for name, pin in manifest['files'].items():
        assert digest(capture / name) == pin['sha256'], name
    qualified = json.loads((root / 'experiments/uart0-repair/results.json').read_text())
    assert qualified['software_qualification_passed']
    assert digest(capture / 'test.bin') == qualified['menu_sha256']
    assert digest(capture / 'repair.bin') == qualified['native_sha256']
    assert digest(capture / 'root-MOS.bin') == 'd564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae'
    assert b'physical_receiver=1' in (capture / 'suite.cfg').read_bytes()
    index = (capture / 'runs.log').read_bytes()

    def journal(run, passed=False):
        data = (capture / f'R{run:04d}.log').read_bytes()
        assert index.count(data) == 1
        text = data.decode()
        assert f'run={run:04d} action=' in text
        assert 'board=Heber Agon Console8 MOS_ROM128K_CRC32=239097B7 API=1.1' in text
        if passed:
            assert f'END run={run:04d} PASS\r\n' in text
            assert not re.search(r'^(?:TEST|END) .* (?:FAIL|SKIP|PENDING)\r?$', text, re.M)
        return text

    paired = {}
    for fixed, run in enumerate((baseline_run, fixed_run)):
        data = (capture / f'U{run:04d}.dat').read_bytes()
        result = analyze(data)
        assert result['regression_passed'] and result['receiver_fixed'] == bool(fixed)
        assert (capture / f'O{run:04d}.dat').read_bytes() == data
        assert not (capture / f'V{run:04d}.dat').exists()
        rx = (capture / f'L{run:04d}.dat').read_bytes()
        assert len(rx) == 3 and rx[0] == 0
        text = journal(run, True)
        native = (capture / 'repair.bin').read_bytes()
        assert f'expected_fixed={fixed} native_bytes={len(native)} native_CRC32={zlib.crc32(native):08X}' in text
        assert f'RXFIX_SCOPE physical_target=1 expected_fixed={fixed} evidence_valid=1' in text
        assert f'TEST {13 + fixed} PASS' in text
        for case in result['cases']:
            token = f"RXFIX fixed={fixed} mode={case['mode']} outcome={case['outcome']} valid=1 rescued={int(case['rescued'])} received={case['received']} CRC={case['crc32']} RX=00"
            assert token in text
        # Attribution is established by this wrapper's physical journal/identity checks.
        result.pop('physical_repair_verified')
        paired['fixed' if fixed else 'baseline'] = dict(run=run, **result)

    assert baseline_run < fixed_run < candidate_run < restore_run
    text = journal(candidate_run, True)
    assert re.findall(r'^TEST (\d+) PASS\r?$', text, re.M) == ['1', '6', '2', '3', '10', '15']
    assert 'VDP=RX-sync-candidate' in text
    assert 'RECOVERY_SCOPE RX-sync-candidate using normal stock commands' in text
    diag = (capture / f'D{candidate_run:04d}.dat').read_bytes()
    assert len(diag) == 12 and diag[3] == diag[6] == diag[9] == 0
    assert diag[2] == diag[5] == diag[8] == diag[11] == 0
    integration = (capture / f'I{candidate_run:04d}.dat').read_bytes()
    u24 = lambda b, at: int.from_bytes(b[at:at + 3], 'little')
    assert len(integration) == 21 and integration[:9] == b'UART0MOS\0'
    assert [u24(integration, at) for at in (9, 12, 15)] == [128, 4110, 128]
    assert integration[18] == 0 and integration[20] == 63
    for prefix in ('N', 'P'):
        data = (capture / f'{prefix}{candidate_run:04d}.dat').read_bytes()
        assert len(data) == 3 and data[0] == 0
    bench_expected = json.loads((capture / 'bench.json').read_text())
    data = (capture / f'B{candidate_run:04d}.dat').read_bytes()
    assert len(data) == 148 and data[:12] == b'UART0BN1\x01\x00\x08\x00'
    bench = []
    for n in range(8):
        r = data[12 + n * 17:29 + n * 17]
        assert r[0] == ((n // 2) ^ (n % 2)) % 2 and r[1] == n // 2
        assert u24(r, 5) == bench_expected['work_checksum']
        assert u24(r, 11) == bench_expected['packet_bytes'] and r[14] == r[16] == 0
        overlap = u24(r, 8)
        assert 1 <= overlap <= bench_expected['work_iterations'] if r[0] else overlap == 0
        bench.append(dict(mode=r[0], pair=r[1], raw_ticks=u24(r, 2), overlap_iterations=overlap,
                          accepted=u24(r, 11), rx_errors=r[14], receiver_result=r[16]))
    stress_expected = json.loads((capture / 'stress.json').read_text())
    data = (capture / f'S{candidate_run:04d}.dat').read_bytes()
    assert len(data) == 76 and data[:12] == b'UART0ST1\x01\x00\x04\x00'
    stress = []
    for n in range(4):
        r = data[12 + n * 16:28 + n * 16]
        assert r[0] == stress_expected['pause_frames'][n] and r[1] == r[2] == 32
        assert 1 <= r[3] <= 32 and u24(r, 4) == stress_expected['packet_bytes'][n]
        assert r[10] == r[12] == r[14] == r[15] == 0 and r[13] == 47
        stress.append(dict(pause_frames=r[0], ordered_replies=r[2], replies_while_busy=r[3],
                           accepted=u24(r, 4), raw_ticks=u24(r, 7), rx_errors=r[10]))
    for prefix in ('B', 'S'):
        name = f'{prefix}{candidate_run:04d}.dat'
        assert f'REPORT {name} hex={(capture / name).read_bytes().hex().upper()}' in text
    spec = importlib.util.spec_from_file_location('recovery_report', root / 'experiments/uart0-recovery/analyze.py')
    recovery_reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recovery_reader)
    data = (capture / f'Y{candidate_run:04d}.dat').read_bytes()
    assert (capture / f'Z{candidate_run:04d}.dat').read_bytes() == data
    recovery = recovery_reader.analyze(data)
    assert recovery['campaign_passed'] and recovery['state']['completed'] == 6
    for case in recovery['records']:
        token = f"RECOVERY case={case['case']} mode={case['mode']} kind={case['kind']} ticks={case['ticks']} wire={case['wire_bytes']} final_verified=8192 replies={case['replies']} overlap_replies={case['replies_while_busy']} rx=00"
        assert token in text
    for prefix in ('C', 'F', 'G', 'J', 'K'):
        assert not (capture / f'{prefix}{candidate_run:04d}.dat').exists()
    restore = journal(restore_run)
    assert 'FLASH_REQUEST target=VDP file=vdp-2.16.0.bin bytes=1077840 CRC32=FFFBFADE' in restore
    assert 'FLASH_RETURN code=0 result=UNVERIFIED' in restore
    assert record['operator_stock_restoration_confirmed']
    return dict(target='Heber Agon Console8', physical_test_performed=True,
        controlled_baseline_fault_captured=paired['baseline']['baseline_fault_captured'],
        physical_repair_verified=paired['fixed']['repaired_without_rescue'],
        repaired_case_payload_bytes_checked=8192, repaired_case_RX_errors=0,
        repaired_cases_rescued=0, candidate_compatibility_passed=True,
        stock_VDP_restored_operator_confirmation=True, stock_restore_run=restore_run,
        natural_stock_failure_reproduced=False, natural_failure_frequency_measured=False,
        performance_requalification_complete=False, release_qualified=False,
        physical_duration_measured=False, SD_writes=False, prior_reports_preserved=True,
        firmware_identity_source='Pinned staged images plus variant/candidate protocol gates; no independent firmware readback',
        candidate_run=candidate_run, candidate_phases_passed=[1, 6, 2, 3, 10],
        candidate=dict(diagnostics_hex=diag.hex(), integration_hex=integration.hex(),
                       benchmark=bench, stress=stress, recovery=recovery),
        paired=paired, evidence_capture=str(capture), fixture_menu_sha256=qualified['menu_sha256'],
        native_sha256=qualified['native_sha256'], capture_manifest_sha256=digest(capture / 'capture.json'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('capture', type=Path)
    for name in ('baseline', 'fixed', 'candidate', 'restore'):
        parser.add_argument('--' + name, required=True, type=int)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    result = inspect(args.capture.resolve(strict=True), args.baseline, args.fixed, args.candidate, args.restore)
    with args.out.open('x') as output:
        json.dump(result, output, indent=2)
        output.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('paired', 'candidate')}, indent=2))
