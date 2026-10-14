"""Collect final fixture evidence while retaining physical-attribution limits."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/uart0-recovery'
read=lambda p:json.loads(p.read_text())
engines={e:read(build/f'checks-{e}/receipt.json') for e in ('jit','interp')}
controls={c:read(build/f'checks-jit-{c}/receipt.json') for c in ('corrupt','noreply')}
interactive=read(build/'checks-interactive/receipt.json')
assert all(r['fixture_checks_passed'] and r['result']['campaign_passed'] for r in engines.values())
assert all(r['control_rejected'] for r in controls.values()) and interactive['short_and_extended_passed']
for r in [*engines.values(),*controls.values(),interactive]:
    assert r['native_sha256']==hashlib.sha256((build/'recovery.bin').read_bytes()).hexdigest()
    assert r['menu_sha256']==hashlib.sha256((build/'test.bin').read_bytes()).hexdigest()
result=dict(fixture_checks_passed=True,automated_release_qualification_passed=False,human_review_passed=False,
 physical_run_performed=False,physical_race_ruled_out=False,receiver_race_attributed=False,known_receiver_race_cleared=False,
 target='Heber Agon Console8',stock_VDP_required='Official 2.16.0 unchanged; operator confirmed',MOS_file_sha256=engines['jit']['rom_sha256'],
 native_sha256=hashlib.sha256((build/'recovery.bin').read_bytes()).hexdigest(),menu_sha256=hashlib.sha256((build/'test.bin').read_bytes()).hexdigest(),
 header_bytes=32,report_bytes=608,short_cases=6,extended_cases=24,short_final_payload_bytes_checked=49152,extended_final_payload_bytes_checked=196608,
 intermediate_bulk_payloads_verified=False,emulator_uses_official_release_VDP_binary=False,
 engines=engines,controls=controls,interactive=interactive,
 initial_failed_setup='The first run rejected emulator zero-filled ROM tail (2A87C5B5) versus physical erased tail (239097B7). Corrected gate explicitly recognizes both identities for the same old ABI1.1 image; this was not a receiver failure.',
 deployment_pending=True,source_checkpoint_before_work='0bda05b',new_work_committed=False)
receipt=build/'deployment.json'
if receipt.exists():
    deployment=read(receipt)
    assert deployment['verified'] and not deployment['physical_firmware_writes']
    result.update(deployment_pending=False,deployment_receipt='build/uart0-recovery/deployment.json',
      stable_SD_entry='/test/mos-uart0/test.bin',SD_UUID='8658-1C23',manual_Console8_run_pending=True)
physical=root/'experiments/uart0-recovery/physical-results.json'
if physical.exists():
    returned=read(physical)
    assert returned['hardware_runs_passed'] and returned['total_cases']==30
    assert returned['native_sha256']==result['native_sha256']
    assert returned['fixture_menu_sha256']==result['menu_sha256']
    result.update(physical_run_performed=True,manual_Console8_run_pending=False,
      physical_return='experiments/uart0-recovery/physical-results.json',
      physical_workload_runs_passed=True,HW_001_preparation_and_return_complete=True)
(root/'experiments/uart0-recovery/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('fixture_checks_passed','physical_run_performed','short_cases','extended_cases','native_sha256','menu_sha256')},indent=2))
