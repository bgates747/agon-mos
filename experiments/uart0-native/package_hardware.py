"""Prepare the reviewed native sender for the stable Console8 suite directory."""
import hashlib,json,shutil,zlib
from pathlib import Path

root=Path(__file__).resolve().parents[2];build=root/'build/uart0-native'
native=Path.home()/'Agon/mystuff/worktrees/uart-native-001/uart'
base=root/'build/uart0-branding/console8-branded';out=build/'console8-native'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(native/'.build/uart-010-final/bin/MOS.bin') != '5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9', 'Historical package withdrawn: N-007 baud-rate boot failure; prepare a newly qualified replacement'
assert not out.exists();shutil.copytree(base,out)
for name in ('manifest.json','SHA256SUMS'):(out/name).unlink()
for suffix in ('bin','map'):shutil.copyfile(native/'.build/uart-010-final/bin'/('MOS.'+suffix),out/('mos-candidate.'+suffix))
assert sha(out/'mos-candidate.bin')=='5543d6acaa64bebd3006cb034a8dda9b61cfe92c82cbbffe2c391a9392f0f4c9'
shutil.copyfile(build/'hardware-menu/test.bin',out/'test.bin')
shutil.copyfile(native/'.build/clients-003/stress16.bin',out/'stress.bin')
assert (out/'stress.bin').read_bytes()[64:73]==b'MOS\x00\x01UBD1'
(out/'suite.cfg').write_text('board=Heber Agon Console8\nmos=mos-candidate.bin\nvdp=vdp-rx-fixed.bin\nvdp_label=RX sync candidate (confirm installed banner)\nvdp_flash=1\nvdp_restore=vdp-2.16.0.bin\nphysical_receiver=1\n')
(out/'readme.txt').write_text('NATIVE MOS UART0 TEST - same directory, new MOS REQUIRED.\r\n'
 'CD /test/mos-uart0\r\nLOAD test.bin\r\nRUN .\r\n'
 '9 then 3: back up installed MOS. 9 then 1: flash mos-candidate.bin.\r\n'
 'Reboot: require Arthur - UART0 OTIRX EXPERIMENTAL ABI1.2.\r\n'
 'Suite must show installed MOS CRC5B36B5B1 and API1.2.\r\n'
 '9 then 7: install supplied repaired VDP candidate; reboot and confirm RX sync candidate banner.\r\n'
 'Reopen suite; choose3 for the reviewed native16-byte full-duplex test.\r\n'
 'Four progress cases; normally about one minute. Over2 minutes/stall is FAIL: reset and report last line.\r\n'
 'Expect four Case PASS lines and suite PASS; repeat3 once to check fresh numbered reports.\r\n'
 'Optional1/6 check API and compatibility. 0 runs applicable baseline tests.\r\n'
 'Old8-submenu receiver investigations require old ABI1.1 MOS; do not use them here.\r\n'
 'Reports/log numbering continues; return card after tests. 9 then4 restores supplied stock VDP2.16.0.\r\n'
 'Do not flash /MOS.bin: it is unchanged stock. No firmware is flashed automatically.\r\n')
raw=(out/'mos-candidate.bin').read_bytes()
identity=dict(ABI='1.2',bytes=len(raw),sha256=sha(out/'mos-candidate.bin'),file_CRC32=f'{zlib.crc32(raw):08X}',ROM128K_CRC32=f'{zlib.crc32(raw+bytes([255])*(131072-len(raw))):08X}')
(out/'firmware.txt').write_text('Native MOS: mos-candidate.bin, API1.2, file CRC'+identity['file_CRC32']+', installed ROM CRC5B36B5B1.\r\n'
 'Menu9/1 installs MOS;9/3 backs up installed MOS first. New MOS is required.\r\n'
 'Menu9/7 installs vdp-rx-fixed.bin (RX sync candidate, no timing/rescue hooks).\r\n'
 'Menu9/4 restores supplied official VDP2.16.0. Reboot and confirm banner after each update.\r\n'
 'Updater return0 alone is UNVERIFIED. Any updater error is FAIL.\r\n'
 'Use the existing Console8 manual recovery procedure if an update fails.\r\n')
(out/'native-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
manifest=json.loads((base/'manifest.json').read_text())
manifest.pop('branded_MOS',None)
manifest.update(native_MOS=identity,MOS_file_sha256=identity['sha256'],
 native_regular_MOS=True,native_stress_batch=16,physical_qualification=False,
 automated_qualification_passed=False,menu_integration_passed=False,
 human_review_passed=False,native_child_human_review_passed=True,
 native_menu_human_review_pending=True,hardware_test_authorization='Author passed native child emulator review and requested Console8 card deployment on2026-10-16',
 expected_card_predecessor_manifest_sha256='5c606c70efd7a334b377b9d7e64fd296153ab716edb6141e4d57e0bd2d84d993')
manifest['files']={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(out.iterdir())}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(sha(p)+'  '+p.name+'\n' for p in sorted(out.iterdir()) if p.name!='SHA256SUMS'))
print(out)
