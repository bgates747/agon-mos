"""Durable evidence summary; prepared diagnostic is not physical qualification."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-race'
read=lambda p:json.loads(p.read_text())
names=('jit','interp','jit-menu','interp-menu','jit-badcrc','jit-noend','jit-nohello','interactive')
checks={n:read(b/f'checks-{n}/receipt.json') for n in names}
assert all(checks[n]['protocol_integrity_passed'] and checks[n]['result']['diagnostic_evidence_valid'] for n in names[:4])
assert all(checks[n]['control_rejected'] for n in names[4:7]) and checks['interactive']['interactive_checks_passed']
audit=read(b/'audit.json');assert audit['driver_override_linked']
result=dict(fixture_checks_passed=True,physical_test_performed=False,physical_race_reproduced=False,
 natural_stock_failure_reproduced=False,physical_race_ruled_out=False,receiver_repair_verified=False,
 release_qualified=False,human_emulator_review_passed=False,HW_002_manual_run_pending=True,
 ownership='This MOS agent owns VDP firmware and MOS test; Flexe owns emulator',
 pre_work_checkpoint='0e01958',new_work_committed=False,checks=checks,audit=audit,
 diagnostic_window_max_CCOUNT_cycles=2400000,pinned_CPU_MHz=240,
 scenarios=['normal recovery without ISR timing pause','bounded delayed ISR after full publication'],
 per_case_payload_bytes=4096,payload_crc32='87897582',receiver_report_bytes=160,host_report_bytes=332,
 source_copy_idf_version='4.4.6',source_VDP_version='2.16.0',
 installed_MOS_unchanged=True,required_MOS_ROM_CRC32='239097B7',
 files={n:hashlib.sha256((b/n).read_bytes()).hexdigest() for n in ('race.bin','test.bin','firmware/.pio/build/esp32dev/firmware.bin')},
 initial_failures=['First generated assembly contained a literal newline escape; ZDS II rejected it before linking. Corrected source assembled and qualified.',
 'First corruption-control checker looked for backend stats before emulator shutdown; stats are emitted at exit. Failure is retained; corrected checker passes controls.'])
receipt=b/'deployment.json'
if receipt.exists():
    deployment=read(receipt);assert deployment['verified'] and not deployment['physical_firmware_writes']
    result.update(SD_staging_verified=True,SD_UUID='8658-1C23',stable_entry='/test/mos-uart0/test.bin',deployment_receipt='build/uart0-race/deployment.json',firmware_flashing_performed=False)
(root/'experiments/uart0-race/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('checks','audit')},indent=2))
