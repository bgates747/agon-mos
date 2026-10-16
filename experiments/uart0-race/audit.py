"""Verify actual driver linkage and keep original/diagnostic disassembly."""
import hashlib,json,subprocess
from pathlib import Path
from analyze import analyze
root=Path(__file__).resolve().parents[2];b=root/'build/uart0-race'
packages=Path.home()/'.platformio/packages'
sdk=packages/'framework-arduinoespressif32@3.20014.231204'
tools=packages/'toolchain-xtensa-esp32@8.4.0+2021r2-patch5/bin'
fw=b/'firmware/.pio/build/esp32dev';original=b/'original-driver';original.mkdir(exist_ok=True)
library=sdk/'tools/sdk/esp32/lib/libdriver.a'
subprocess.run([str(tools/'xtensa-esp32-elf-ar'),'x',str(library),'uart.c.obj'],cwd=original,check=True)
for src,out in [(original/'uart.c.obj',original/'uart.dis'),(fw/'firmware.elf',b/'linked-driver.dis')]:
    with out.open('w') as f:subprocess.run([str(tools/'xtensa-esp32-elf-objdump'),'-dr',str(src)],stdout=f,check=True)
dis=(original/'uart.dis').read_text()
assert '33e:' in dis and '34b:' in dis and '36a:' in dis
mapping=(fw/'firmware.map').read_text();assert '.pio/build/esp32dev/src/uart0_diag_driver.c.o' in mapping
assert 'libdriver.a(uart.c.obj)' not in mapping,'Uninstrumented archive object linked'
symbols=subprocess.check_output([str(tools/'xtensa-esp32-elf-nm'),str(fw/'firmware.elf')],text=True)
for name in ('uart0_race_arm','uart0_race_collect','uart0_race_snapshot','uart0_race_escape','uart_read_bytes','uart_rx_intr_handler_default'):
    assert len([line for line in symbols.splitlines() if line.endswith(' '+name)])==1,name
source=(b/'uart-idf-4.4.6.c').read_bytes()
assert hashlib.sha256(source).hexdigest()=='0a90ac006b6a0cadaac4c47ab035a54c782fb6171fda82e9dd059a3d84c4b0be'
native=(b/'race.bin').read_bytes();assert len(native)<65536 and native[64:73]==b'MOS\0\1URD1'
for at in (73,89,105,121):assert b'\0' in native[at:at+16]
assert len((b/'test.bin').read_bytes())<65536
# Acceptance oracle must reject intact payloads with contradictory core/state
# evidence; byte integrity alone must never turn a missing ordering into PASS.
data=(b/'checks-jit/attempt-001/race.dat').read_bytes();assert analyze(data)['diagnostic_evidence_valid']
controls=[]
for name,at,value in [('same_core',12+160+88+1,data[12+160+64+1]),('RX_still_enabled',12+160+28,0x95),('recovery_flag_still_set',12+160+36,1)]:
    bad=bytearray(data);bad[at]=value;r=analyze(bad)
    assert r['protocol_complete'] and all(c['integrity_passed'] for c in r['cases']) and not r['diagnostic_evidence_valid']
    controls.append(name)
receipt=dict(driver_override_linked=True,unmodified_archive_driver_excluded=True,
 original_ISR_offsets=dict(publish_full='0x33e',take_lock_call='0x34b',RX_mask_store='0x36a'),
 invalid_evidence_controls_rejected=controls,physical_test_performed=False,
 files={str(p.relative_to(root)) if p.is_relative_to(root) else str(p):hashlib.sha256(p.read_bytes()).hexdigest()
 for p in (library,original/'uart.c.obj',b/'uart-idf-4.4.6.c',fw/'firmware.bin',fw/'firmware.elf',b/'race.bin',b/'test.bin')})
(b/'audit.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
