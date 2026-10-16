"""Real SDL key events: menu, calibration, backup, upstream N-cancel and faults."""
import hashlib,json,os,signal,shutil,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parents[3]
build=root/'build/uart0-suite';profile=root/'.emulator/uart0-suite-keys'
app=profile/'sdcard/uart0';artifacts=profile/'last-run'
artifacts.mkdir(exist_ok=True)
for p in app.iterdir():
    if p.suffix.lower() in ('.dat','.log','.txt','.bin') and (p.name[0].isupper() or p.name=='runs.log'):p.unlink()
for p in artifacts.iterdir():
    if p.is_file():p.unlink()
keys=build/'keys-input';keys.write_bytes(b'')
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
env=dict(os.environ,SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE='jit',LD_PRELOAD=str(build/'keys.so'),UART_SUITE_KEYS=str(keys))
process=None;cursor=0;started=time.monotonic();original=(app/'bench.bin').read_bytes()
original_cfg=(app/'suite.cfg').read_text()
def wire():
    p=artifacts/'mos-to-vdp.bin';return p.read_bytes() if p.exists() else b''
def wait(marker,timeout=75):
    global cursor
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        data=wire();pos=data.find(marker,cursor)
        if pos>=0:cursor=pos+len(marker);return
        if process.poll() is not None:raise RuntimeError('Emulator exited early')
        time.sleep(.05)
    raise TimeoutError(f'Waiting for {marker!r}; tail={wire()[-400:]!r}')
def key(s):
    with keys.open('ab') as f:f.write(s)
def menu():wait(b'Press a choice key:')
def firmware(choice):
    key(b'9');wait(b'0 back');key(choice)
try:
    with (artifacts/'frontend.log').open('w') as output:
        process=subprocess.Popen(['./flexe-agon-emulator','--precise-interrupts'],cwd=profile,env=env,stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        menu();key(b'4');wait(b'Press ESC to skip.')
        key(b'\n');wait(b'Timing active;');time.sleep(10.2);key(b'\n')
        wait(b'Enter stopwatch seconds');key(b'10.200\n');wait(b'Run 0001: PASS');key(b' ');menu()
        firmware(b'3');wait(b'Run 0002: PASS');menu()
        firmware(b'1');wait(b'Flash firmware (y/n)?');key(b'n');wait(b'User abort');wait(b'FLASH RESULT UNVERIFIED');menu()
        firmware(b'2');wait(b'Flash firmware (y/n)?');key(b'n');wait(b'User abort');wait(b'FLASH RESULT UNVERIFIED');menu()
        (app/'bench.bin').rename(app/'bench.saved')
        key(b'2');wait(b'Cannot load bench.bin');wait(b'Run 0005: FAIL');key(b' ');menu()
        (app/'bench.saved').rename(app/'bench.bin')
        packet=(build/'bench/expected-packet.bin').read_bytes()
        assert original.count(packet)==1
        bad=bytearray(original);bad[original.index(packet)+14]^=1
        (app/'bench.bin').write_bytes(bad)
        key(b'2');wait(b'Run 0006: FAIL');key(b' ');menu()
        (app/'bench.bin').write_bytes(original)
        (app/'R0007.log').write_text('INTERRUPTED SENTINEL\n')
        (app/'B0008.dat').write_text('ORPHAN RESULT SENTINEL\n')
        key(b'1');wait(b'Run 0009: PASS');key(b' ');menu()
        (app/'R0009.log').unlink();(app/'D0009.dat').unlink()
        key(b'1');wait(b'Run 0010: PASS');key(b' ');menu()
        key(b'q');wait(b'UART0 SUITE RETURN TO MOS');wait(b'/uart0 *')
        # Reload with the human emulator capability setting. No firmware
        # protocol is sent when VDP update support is unavailable.
        (app/'suite.cfg').write_text(original_cfg.replace('vdp_flash=1','vdp_flash=0'))
        key(b'load test.bin\nrun\n');menu()
        firmware(b'2');wait(b'updater not launched.');wait(b'Run 0011: SKIP');menu()
        (app/'flash.bin').rename(app/'flash.saved')
        firmware(b'1');wait(b'Cannot load staged flash.bin.');wait(b'Run 0012: FAIL');menu()
        (app/'flash.saved').rename(app/'flash.bin')
        firmware(b'4');wait(b'updater not launched.');wait(b'Run 0013: SKIP');menu()
        key(b'7');wait(b'SKIP: requires the staged UART0 CTS diagnostic VDP.');wait(b'Run 0014: PENDING');key(b' ');menu()
        key(b'q');wait(b'UART0 SUITE RETURN PASS');wait(b'/uart0 *')
finally:
    (app/'bench.bin').write_bytes(original)
    (app/'suite.cfg').write_text(original_cfg)
    if (app/'flash.saved').exists():(app/'flash.saved').rename(app/'flash.bin')
    (app/'bench.saved').unlink(missing_ok=True)
    if process and process.poll() is None:
        for p in Path('/proc').glob('[0-9]*'):
            try:
                if os.getpgid(int(p.name))==process.pid and (p/'exe').resolve()==(profile/'flexe-agon-emulator.bin').resolve():os.kill(int(p.name),signal.SIGTERM)
            except (FileNotFoundError,PermissionError,ProcessLookupError):pass
        try:process.wait(timeout=10)
        except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
assert process.returncode==0
assert (app/'R0007.log').read_text()=='INTERRUPTED SENTINEL\n'
assert (app/'B0008.dat').read_text()=='ORPHAN RESULT SENTINEL\n'
assert (app/'M0002.bin').stat().st_size==131072
assert (app/'C0001.txt').read_text().startswith('CALIBRATION raw_ticks=')
assert (app/'F0006.dat').read_bytes()[9]==2 and not (app/'B0006.dat').exists()
assert b'Programming MOS firmware' not in wire()
assert b'Programming VDP' not in wire()
assert wire().count(b'User abort')==2
for n,status in [(1,'PASS'),(2,'PASS'),(3,'PENDING'),(4,'PENDING'),(5,'FAIL'),(6,'FAIL'),(10,'PASS'),(11,'SKIP'),(12,'FAIL'),(13,'SKIP'),(14,'PENDING')]:
    log=(app/f'R{n:04d}.log').read_text();assert f'END run={n:04d} {status}' in log,log
for n in (3,4):
    log=(app/f'R{n:04d}.log').read_text()
    assert 'FLASH_RETURN code=0 result=UNVERIFIED' in log and log.count('END run=')==1,log
log=(app/'R0011.log').read_text()
assert 'FLASH_SKIP target=VDP reason=emulator_OTA_not_qualified' in log and 'FLASH_REQUEST' not in log
assert 'FLASH_RETURN result=FAIL reason=utility_load_failed' in (app/'R0012.log').read_text()
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=profile,check=True)
stats=json.loads((artifacts/'stats.json').read_text())
assert not any(stats[k] for k in ('failed','unhandled','unregistered','unmapped')),stats
result=build/'evidence-interactive';result.mkdir(exist_ok=True)
for p in [*artifacts.iterdir(),*app.iterdir()]:
    if p.is_file() and (p.suffix in ('.log','.dat','.txt','.json','.ppm') or p.name=='M0002.bin'):shutil.copyfile(p,result/p.name)
r=dict(elapsed_seconds=round(time.monotonic()-started,3),real_SDL_key_events=True,menu_choices_verified=True,
    calibration_entry_verified=True,calibration_is_simulated_not_physical=True,mos_backup_verified=True,
    real_upstream_MOS_flash_cancelled=True,real_upstream_VDP_flash_cancelled=True,firmware_writes=False,
    missing_fixture_rejected=True,corrupted_payload_rejected_and_returned_to_menu=True,
    interrupted_and_orphan_run_numbers_skipped=True,reserved_run_numbers=[1,2,3,4,5,6,9,10,11,12,13,14],
    stock_VDP_margin_trial_skipped=True,emulator_stock_restore_blocked=True,
    emulator_VDP_flash_blocked_without_launch=True,zero_flash_return_logged_unverified=True,
    missing_flash_utility_logged_FAIL_after_handoff=True,
    numbering_monotonic_after_old_reports_removed=True,
    earlier_results_preserved=True,returned_to_mos=True,graphical_instance_launched=False,
    shim_sha256=hashlib.sha256((build/'keys.so').read_bytes()).hexdigest(),backend=stats,
    runtime_identities=(profile/'.runtime.sha256').read_text().splitlines())
(result/'receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
