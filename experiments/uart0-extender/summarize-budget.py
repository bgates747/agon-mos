"""Summarize saved native EMOS links and ROM readback; no hardware access."""
import argparse
import hashlib
import json
import re
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--build-root', required=True, type=Path)
parser.add_argument('--installed-rom', required=True, type=Path)
parser.add_argument('--sender-map', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rom = args.installed_rom.read_bytes()
assert len(rom) == 131072
assert digest(args.installed_rom) == '6f83bc21558ea7dcb665b60c18aa3a5c3030367f901e3e32ccbbf99eaf7f4019'
extent = len(rom.rstrip(b'\xff'))
assert extent == 128622
rows = []
for attempt in (3, 5, 6, 7):
    root = args.build_root / f'native-baseline-{attempt:03d}'
    log = (root / 'build.log').read_text(errors='replace')
    match = re.search(r'^ROM\s+.*\n\s*\(\s*(\d+)\s+(\d+)\s+(-?\d+)\)', log, re.M)
    assert match and int(match[1]) == 131072
    assert 'ERROR: Object file(s) deleted because of option warning=fatal.' in log
    assert not (root / 'MOS.bin').exists(), 'Unexpected successful image in an overflowing attempt'
    used = int(match[2])
    assert int(match[3]) == 131072 - used
    rows.append(dict(attempt=root.name, native_C_and_assembly_compiled=True,
        link_passed=False, ROM_used_bytes=used, ROM_overflow_bytes=used - 131072,
        log_sha256=digest(root / 'build.log'), map_sha256=digest(root / 'MOS.map')))
sender_map = args.sender_map.read_text()
module = re.search(r'Module: uart0_async\.asm.*?\n(.*?)(?=\nModule:)', sender_map, re.S)
assert module
size = re.search(r'Segment: \.STARTUP\s+C:[\dA-F]+\s+C:[\dA-F]+\s+([\dA-F]+)h', module[1], re.I)
assert size and int(size[1], 16) == 2497
best = min(r['ROM_used_bytes'] for r in rows)
result = dict(assessment_complete=True, integration_implemented=False,
    native_EMOS_fits=False, hardware_test_performed=False, firmware_changed=False,
    toolchain='ZDS II eZ80Acclaim!5.3.5 under Wine on Oryx',
    source_baseline='cf10f0b1848346bc5d04056e4663bbbc166b2480',
    native_compatibility_changes=['Structure copy initialization uses explicit memcpy',
                                  'Command fallback declarations precede executable statements'],
    installed_saved_ROM_bytes=len(rom), installed_payload_extent_bytes=extent,
    installed_trailing_erased_bytes=len(rom) - extent,
    installed_saved_ROM_sha256=digest(args.installed_rom),
    native_attempts=rows, best_native_ROM_used_bytes=best,
    best_native_ROM_overflow_bytes=best - 131072,
    generic_sender_module_ROM_bytes=int(size[1], 16), sender_map_sha256=digest(args.sender_map),
    simple_additive_budget_gap_bytes=best + int(size[1], 16) - 131072,
    additive_gap_is_not_an_integrated_link=True,
    budget_limit='Final integration also adds hooks and replaces some existing code; measure actual link rather than promise an exact saving',
    existing_diagnostic_MOSlet_reference='agon-emos commits c98f80e and8f06429',
    diagnostic_backport_size_measured=False, toolchain_exception_authorized=False,
    recommendation='Keep ZDS II and first scope measured EMOS ROM compaction, starting with existing owner-designed diagnostic MOSlets; preserve input, SD and routing; do not flash overflowing code',
    execution_state='Stopped for Author review; no automatic continuation')
with args.out.open('x') as output:
    json.dump(result, output, indent=2)
    output.write('\n')
print(json.dumps(result, indent=2))
