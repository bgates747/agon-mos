"""Run unchanged native code without debugger overhead; capture after a stall."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

root = Path(__file__).resolve().parents[2]
p = root/'.emulator/uart0-ab-auto'
art = p/'last-run'
base = root/'build/uart0-ab/host-stalls'
base.mkdir(exist_ok=True)
for procdir in Path('/proc').glob('[0-9]*'):
    try:
        if (procdir/'exe').resolve() == (p/'runtime/flexe-agon-emulator.bin').resolve():
            raise RuntimeError('Auto profile is already running')
    except (FileNotFoundError,PermissionError):
        pass
subprocess.run(['sha256sum','--check','--status','.runtime.sha256'],cwd=p,check=True)
engine = sys.argv[1] if len(sys.argv)>1 else 'jit'
assert engine in ('jit','interp')
precise = len(sys.argv) < 4 or sys.argv[3] != 'coarse'
for _ in range(int(sys.argv[2]) if len(sys.argv)>2 else 4):
    number = 1
    while (base/f'attempt-{number:03d}').exists():
        number += 1
    dest = base/f'attempt-{number:03d}'
    dest.mkdir()
    for f in [*art.iterdir(),*(p/'sdcard/uart0').glob('*.dat')]:
        if f.is_file():
            f.unlink()
    for name in ['app.map','app.lst','test.bin']:
        shutil.copyfile(root/'build/uart0-ab/native'/name,dest/name)
    shutil.copyfile(p/'.runtime.sha256',dest/'runtime.sha256')
    video = os.environ.get('UART_AB_VIDEO','dummy')
    assert video in ('dummy','x11')
    env = dict(os.environ,SDL_VIDEODRIVER=video,SDL_AUDIODRIVER='dummy',AGON_FLEXE_ENGINE=engine)
    start = changed = time.monotonic()
    size = -1
    reason = 'deadline'
    data = b''
    watcher = None
    watcher_log = None
    with (art/'frontend.log').open('w') as log:
        proc = subprocess.Popen(['./fab-agon-emulator'] + (['--precise-interrupts'] if precise else []),cwd=p,
                                env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            while time.monotonic()-start < 180:
                path = art/'mos-to-vdp.bin'
                data = path.read_bytes() if path.exists() else b''
                if os.environ.get('UART_AB_WATCH_RX')=='1' and watcher is None and b'A/B repeat 1 mode 1 phase 0' in data:
                    targets = []
                    for d in Path('/proc').glob('[0-9]*'):
                        try:
                            if os.getpgid(int(d.name))==proc.pid and (d/'exe').resolve()==(p/'flexe-agon-emulator.bin').resolve():
                                targets.append(int(d.name))
                        except (FileNotFoundError,PermissionError,ProcessLookupError):
                            pass
                    assert len(targets)==1,targets
                    watcher_log = (dest/'watch-gdb.log').open('w')
                    watcher = subprocess.Popen(['sudo','-n','env',f'UART_AB_CAPTURE={dest}','gdb','-q','-batch',
                        '-p',str(targets[0]),'-ex',f'source {root}/experiments/uart0-ab/watch_rx.py',
                        '-ex','continue','-ex',f'source {root}/experiments/uart0-ab/capture_host.py','-ex','detach'],
                        stdout=watcher_log,stderr=subprocess.STDOUT)
                if watcher is not None and watcher.poll() is not None:
                    history = dest/'rx-write-history.json'
                    if history.exists() and json.loads(history.read_text())['anomaly']:
                        reason = 'rx_mask_ordering'
                        break
                    raise RuntimeError('RX watch ended without a captured anomaly; inspect watch-gdb.log')
                if b'UART0 AB MOS RETURN' in data:
                    reason = 'returned'
                    break
                if len(data) != size:
                    size = len(data)
                    changed = time.monotonic()
                if time.monotonic()-changed > 15:
                    reason = 'no_tx_progress'
                    break
                if proc.poll() is not None:
                    reason = 'exited'
                    break
                time.sleep(.25)
            if watcher is not None and watcher.poll() is None:
                subprocess.run(['sudo','-n','kill','-INT',str(watcher.pid)],check=True)
                try:
                    watcher.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    subprocess.run(['sudo','-n','kill','-TERM',str(watcher.pid)],check=True)
                    watcher.wait(timeout=10)
            if (reason != 'returned' or os.environ.get('UART_AB_CAPTURE_RETURN')=='1') and proc.poll() is None:
                targets = []
                for d in Path('/proc').glob('[0-9]*'):
                    try:
                        if os.getpgid(int(d.name)) == proc.pid and (d/'exe').resolve() == (p/'flexe-agon-emulator.bin').resolve():
                            targets.append(int(d.name))
                    except (FileNotFoundError,PermissionError,ProcessLookupError):
                        pass
                assert len(targets)==1,targets
                for index in range(1 if reason=='returned' else 2):
                    snapshot = dest if index==0 else dest/'second-snapshot'
                    if index:
                        snapshot.mkdir()
                        shutil.copyfile(dest/'test.bin',snapshot/'test.bin')
                        time.sleep(.2)
                    command = ['sudo','-n','env',f'UART_AB_CAPTURE={snapshot}','gdb','-q','-batch',
                               '-p',str(targets[0]),'-ex',f'source {root}/experiments/uart0-ab/capture_host.py',
                               '-ex','detach']
                    with (snapshot/'gdb.log').open('w') as capture:
                        subprocess.run(command,stdout=capture,stderr=subprocess.STDOUT,check=True,timeout=30)
                    assert (snapshot/'capture-complete.json').exists(),'Incomplete host capture; inspect gdb.log'
                    if (snapshot/'cpu-state.json').exists():
                        subprocess.run([sys.executable,'-B',str(root/'experiments/uart0-ab/analyze_stall.py'),str(snapshot)],
                                       check=True,stdout=subprocess.DEVNULL)
                if reason!='returned' and os.environ.get('UART_AB_RECOVER_RX')=='1':
                    assert json.loads((dest/'analysis.json').read_text())['receive_wakeup_failure']
                    command = ['sudo','-n','env',f'UART_AB_CAPTURE={dest}','gdb','-q','-batch',
                               '-p',str(targets[0]),'-ex',f'source {root}/experiments/uart0-ab/recover_rx.py',
                               '-ex','detach']
                    with (dest/'recovery-gdb.log').open('w') as capture:
                        subprocess.run(command,stdout=capture,stderr=subprocess.STDOUT,check=True,timeout=30)
                    time.sleep(1)
                    after = (art/'mos-to-vdp.bin').read_bytes()
                    (dest/'recovery-result.json').write_text(json.dumps(dict(
                        qualification=False,tx_before=len(data),tx_after=len(after),
                        tx_progress=len(after)>len(data)),indent=2)+'\n')
        finally:
            if watcher is not None and watcher.poll() is None:
                subprocess.run(['sudo','-n','kill','-TERM',str(watcher.pid)],check=True)
                watcher.wait(timeout=10)
            if watcher_log is not None:
                watcher_log.close()
            if proc.poll() is None:
                for d in Path('/proc').glob('[0-9]*'):
                    try:
                        if os.getpgid(int(d.name))==proc.pid and (d/'exe').resolve()==(p/'flexe-agon-emulator.bin').resolve():
                            os.kill(int(d.name),signal.SIGTERM)
                    except (FileNotFoundError,PermissionError,ProcessLookupError):
                        pass
                proc.wait(timeout=10)
            for f in [*art.iterdir(),*(p/'sdcard/uart0').glob('*.dat')]:
                if f.is_file():
                    shutil.copyfile(f,dest/f.name)
            outcome = dict(engine=engine,video=video,precise_interrupts=precise,reason=reason,elapsed_seconds=time.monotonic()-start,
                           tx_bytes=len(data),last_phase=repr(data.split(b'A/B repeat')[-1][:32]),
                           exit_code=proc.returncode)
            (dest/'outcome.json').write_text(json.dumps(outcome,indent=2)+'\n')
            print(json.dumps(dict(artifact_directory=str(dest.relative_to(root)),**outcome)),flush=True)
    if reason != 'returned':
        break
