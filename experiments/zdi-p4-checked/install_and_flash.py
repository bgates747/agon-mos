#!/usr/bin/env python3
"""Run normal checked stock-MOS recovery through the selected P4.

P4 backup and programmer installation checks concern the programmer only.
The eZ80 identity and MOS RAM/post-flash CRC checks follow upstream.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import time

MOS_SHA = 'd564243283972690933a4554296ad6202ca4ef54572279533a942960846bebae'
AGENT_SHA = 'ca44786969dc2dd1b0fa51e6b80f530b7241317dc27bf8efac3ca7d56bddee06'


def main():
    import serial
    from esptool.reset import HardReset

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port', type=Path, required=True)
    p.add_argument('--serial-id', required=True)
    p.add_argument('--app', type=Path, required=True)
    p.add_argument('--mos', type=Path, required=True)
    p.add_argument('--agent', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    mos, agent, app = a.mos.read_bytes(), a.agent.read_bytes(), a.app.read_bytes()
    sha = lambda data: hashlib.sha256(data).hexdigest()
    assert len(mos) == 108490 and sha(mos) == MOS_SHA
    assert len(agent) == 90 and sha(agent) == AGENT_SHA
    assert app[0] == 0xE9 and app.count(mos) == 1 and agent in app
    assert b'P4-CHECKED r01' in app
    props = subprocess.check_output(
        ['udevadm', 'info', '--query=property', '--name', str(a.port.resolve(strict=True))],
        text=True)
    assert 'ID_SERIAL_SHORT=' + a.serial_id + '\n' in props
    a.out.mkdir(parents=True, exist_ok=False)
    result = dict(payload_sha256=MOS_SHA, programmer_sha256=sha(app),
                  checks_restored=True, flash_command_sent=False,
                  sequence_finished=False, flash_verified=False,
                  boot_confirmed=False, P4_restoration_deferred=True,
                  automatic_retry=False)
    started = time.monotonic()

    def checkpoint():
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        (a.out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')

    def tool(label, before, after, args):
        argv = [sys.executable, '-m', 'esptool', '--chip', 'esp32p4', '--port', str(a.port),
                '--before', before, '--after', after] + args
        (a.out / (label + '-argv.json')).write_text(json.dumps(argv, indent=2) + '\n')
        print(label, flush=True)
        with (a.out / (label + '.log')).open('x') as log:
            subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)

    handle = None
    try:
        # Prior full P4 backup and exact installed write-only binary are retained.
        # Preserve/verify that known current application before replacing it.
        prior = a.out.parent.parent / 'p4-flash-only-20261030/artifacts/p4-flash-only-r01.bin'
        assert sha(prior.read_bytes()) == '61bb640eaf05fcd8e5f90349fb4f2a5de44d5afb2453e581bf434e7d8191693e'
        tool('p4-prior-programmer-verify', 'usb_reset', 'no_reset',
             ['verify_flash', '0x20000', str(prior)])
        result['prior_programmer_sha256'] = sha(prior.read_bytes())
        checkpoint()
        tool('p4-programmer-write', 'no_reset', 'no_reset',
             ['write_flash', '--flash_mode', 'keep', '--flash_freq', 'keep',
              '--flash_size', 'keep', '0x20000', str(a.app)])
        tool('p4-programmer-verify', 'no_reset', 'no_reset',
             ['verify_flash', '0x20000', str(a.app)])
        result['P4_programmer_verified'] = True
        checkpoint()
        handle = serial.Serial(port=None, baudrate=115200, timeout=.2, write_timeout=3)
        handle.dtr = False
        handle.rts = False
        handle.port = str(a.port)
        handle.open()
        HardReset(handle, uses_usb=True)()
        deadline = time.monotonic() + 120
        raw = bytearray()
        with (a.out / 'console.log').open('xb', buffering=0) as log:
            while time.monotonic() < deadline:
                chunk = handle.readline()
                if not chunk:
                    continue
                log.write(chunk)
                raw.extend(chunk)
                print(chunk.decode('ascii', errors='replace'), end='', flush=True)
                if any(term in raw for term in
                       (b'Guru Meditation', b'abort()', b'task_wdt:', b'assert failed')):
                    raise RuntimeError('P4 programmer fault; no automatic retry')
                if (b'READY P4-CHECKED r01 GREEN=46 BLUE=47' in chunk
                        and not result['flash_command_sent']):
                    assert ('Payload 108490 bytes SHA256 ' + MOS_SHA).encode() in raw
                    # This is the only application command sent to the P4.
                    handle.write(b'FLASH\n')
                    handle.flush()
                    result['flash_command_sent'] = True
                    checkpoint()
                if chunk.startswith(b'RESULT '):
                    assert result['flash_command_sent']
                    outcome = chunk.decode().strip().split()[1]
                    result['outcome'] = outcome
                    result['flash_agent_started'] = b'Executing flash agent;' in raw
                    result['flash_verified'] = outcome == 'flash_crc_pass'
                    result['sequence_finished'] = True
                    result['console_sha256'] = sha(raw)
                    break
            else:
                raise TimeoutError('Checked programmer did not finish; no automatic retry')
    except BaseException as exc:
        result['error'] = repr(exc)
        raise
    finally:
        if handle is not None and handle.is_open:
            handle.close()
        checkpoint()
        print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
