"""Archive passing checks and the retained qualification failure together."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-batching'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
model={}
for mode in ('scalar','otirx'):
    for n in (1,2,4,8,16):
        p=b/f'checks-{mode}-{n}.txt';text=p.read_text();assert f'PASS batch={n}: 2364 ' in text
        model[f'{mode}-{n}']=dict(scenarios=2364,result_sha256=sha(p),image_sha256=sha(b/mode/'driver.bin'))
controls={}
for mode in ('scalar','otirx'):
    for fault,reason in (('bad-guard','CTS group allowance exceeded'),('burst','burst exceeds 16'),('release','early source release')):
        p=b/f'negative-{mode}-{fault}.log';assert reason in p.read_text();controls[f'{mode}-{fault}']=dict(rejected=True,reason=reason,result_sha256=sha(p))
production={}
for n in (1,2,4,8,16):
    p=b/f'production-{n}.txt';s=p.read_text();assert 'PASS 27 production-ROM' in s and 'PASS production batch controls 538 cases' in s
    production[str(n)]=dict(integration_scenarios=27,batch_control_scenarios=538,result_sha256=sha(p))
final={e:json.loads((b/f'evidence-{e}/receipt.json').read_text()) for e in ('jit','interp')}
for e,receipt in final.items():
    assert receipt['returned_to_mos'] and receipt['crc_payload_bytes']==40960 and receipt['receiver_bytes_compared']==163840
    assert not receipt['physical_qualification'] and not receipt['known_receiver_race_cleared']
    expected=sha(b/'native/test.bin');assert f'{expected}  sdcard/uart0/test.bin' in receipt['runtime_identities']
    for n in (1,2,4,8,16):assert f'{sha(b/f"native/stress{n}/test.bin")}  sdcard/uart0/stress{n}.bin' in receipt['runtime_identities']
negatives={name:json.loads((b/f'evidence-jit-{name}/receipt.json').read_text()) for name in ('crc','noend')}
assert all(r['rejected'] for r in negatives.values())
baseline={e:json.loads((b/f'baseline-{e}/receipt.json').read_text()) for e in ('jit','interp')}
failure=json.loads((b/'stall-001/analysis.json').read_text())
result=dict(experimental=True,abi='1.2',automated_qualification_passed=False,final_native_protocol_checks_passed=True,
    known_receiver_race_cleared=False,human_review_passed=False,physical_qualification=False,sd_written=False,
    gate='A captured combined JIT stall retains AB-006 receiver-owner correction/regression gate; later passing runs do not clear it',
    core_sha256=sha(b/'source/uart0_tx.inc'),wrapper_sha256=sha(b/'source/uart0_async.asm'),
    rom_sha256=sha(root/'build/uart0-mos/MOS.bin'),rom_bytes=(root/'build/uart0-mos/MOS.bin').stat().st_size,
    scripted=model,scripted_scenarios=23640,batching_fault_controls=controls,production_rom_checks=production,
    baseline_engines=baseline,native_engines=final,native_negative_controls=negatives,retained_failure=failure,
    per_engine_payload_bytes_checked=204800,matched_16KiB_AB_command_integrity_complete=False,
    sequential_menu_integration_complete=False,reporting='Private off-device reports with preserved attempt history; fixed native filename slots prepared for menu integration')
(root/'experiments/uart0-batching/results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ('abi','scripted_scenarios','final_native_protocol_checks_passed','automated_qualification_passed','per_engine_payload_bytes_checked','rom_sha256')},indent=2))
