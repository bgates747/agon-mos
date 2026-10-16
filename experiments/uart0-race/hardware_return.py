"""Validate a preserved Console8 diagnostic return; never access the live SD."""
import argparse,hashlib,json
from pathlib import Path
from analyze import analyze

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('capture',type=Path)
p.add_argument('--run',required=True,type=int)
p.add_argument('--menu-confirmed',action='store_true')
p.add_argument('--stock-restored',choices=('yes','no','unknown'),default='unknown')
p.add_argument('--out',required=True,type=Path)
a=p.parse_args();capture=a.capture.resolve(strict=True)
record=json.loads((capture/'capture.json').read_text())
digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
for name,pin in record['files'].items():assert digest(capture/name)==pin,name
assert record['SD_writes'] is False and record['package_verified'] and record['prior_reports_preserved']
assert record['mount']['uuid'].upper()=='8658-1C23'
manifest=json.loads((capture/'manifest.json').read_text())
assert manifest['target']=='Heber Agon Console8' and manifest['native_checkpoint_fix']
for name,pin in manifest['files'].items():assert digest(capture/name)==pin['sha256'],name
n=f'{a.run:04d}'
data=(capture/f'U{n}.dat').read_bytes();result=analyze(data)
assert result['diagnostic_evidence_valid'] and (capture/f'O{n}.dat').read_bytes()==data
assert not (capture/f'V{n}.dat').exists()
baseline=(capture/f'L{n}.dat').read_bytes();assert len(baseline)==3 and baseline[0]==0
detail=(capture/f'R{n}.log').read_bytes();index=(capture/'runs.log').read_bytes()
assert detail in index
text=detail.decode()
for token in ('MOS_ROM128K_CRC32=239097B7 API=1.1',
              'RACE_SCOPE physical_target=1 evidence_valid=1 diagnostic_induced=1 natural_stock_failure=NOT_ESTABLISHED repair=NOT_TESTED',
              'TEST 12 PASS',f'END run={n} PASS'):
    assert token in text,token
pins={'test.bin':'841045e1b78aa3d6f3191f0bad46c19ef96c50e4ec9f496942201b2c4cef30ac',
      'race.bin':'ac3f8a7ef9bf50e371f3c7319a6c877c4f225b4a489d9f55f22cedcfdef4db3f',
      'vdp-race-diag.bin':'59fe20e7e72c1e5c9b47341c50faf7cb180ac8f6a00755f074be7d44cfab4f0f'}
for name,pin in pins.items():assert digest(capture/name)==pin,name
output=dict(target='Heber Agon Console8',run=a.run,physical_test_performed=True,
    physical_diagnostic_passed=True,diagnostic_induced_physical_ordering_reproduced=True,
    natural_stock_failure_reproduced=False,physical_race_ruled_out=False,
    receiver_repair_verified=False,release_qualified=False,
    payload_bytes_checked=sum(c['received'] for c in result['cases']),
    checkpoint_matches_final=True,menu_and_index_agree=True,case_RX_errors=0,
    baseline_RX_flags=baseline[0],baseline_modem_flags=baseline[1],
    entry_RX_flags='98',entry_RX_origin_traced=False,
    menu_hardware_confirmed=a.menu_confirmed,
    stock_VDP_restored_operator_confirmation=a.stock_restored,
    diagnostic_VDP_still_installed_operator_confirmation=a.stock_restored=='no',
    firmware_identity_source='Diagnostic protocol handshake and byte-checked staged files; no independent flash readback',
    physical_duration_measured=False,SD_writes=False,prior_reports_preserved=True,
    report_sha256=hashlib.sha256(data).hexdigest(),journal_sha256=hashlib.sha256(detail).hexdigest(),
    fixture_pins=pins,evidence_capture=str(capture),
    evidence_archive=f'build/uart0-race-console8-r{n}.tar.gz',result=result)
assert not a.out.exists()
a.out.write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k not in ('result','fixture_pins')},indent=2))
