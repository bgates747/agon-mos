#!/usr/bin/env python3
"""Install the identity-only P4 application and read an attached eZ80 identity.

Only P4 firmware is changed. Target CPU/flash commands do not exist in this image.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


def main():
    import serial
    from esptool.reset import HardReset

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('port', 'app', 'prior', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--serial-id', required=True)
    a = parser.parse_args()
    sha = lambda data: hashlib.sha256(data).hexdigest()
    image = a.app.read_bytes()
    assert image[0] == 0xE9 and b'P4-IDENTITY-ONLY r01' in image
    assert b'FLASH START' not in image and b'Executing flash agent;' not in image
    props = subprocess.check_output(
        ['udevadm', 'info', '--query=property', '--name', str(a.port.resolve(strict=True))],
        text=True)
    assert 'ID_SERIAL_SHORT=' + a.serial_id + '\n' in props
    a.out.mkdir(parents=True, exist_ok=False)
    result = dict(target='Olimex Agon Light 2', target_flash_attempted=False,
                  target_cpu_halt_requested=False, identity_command_sent=False,
                  automatic_retry=False, identities=[], P4_identity_only_retained=True,
                  programmer_sha256=sha(image), prior_programmer_sha256=sha(a.prior.read_bytes()))
    started = time.monotonic()
    reader = None

    def tool(label, before, args):
        argv = [sys.executable, '-m', 'esptool', '--chip', 'esp32p4', '--port', str(a.port),
                '--before', before, '--after', 'no_reset'] + args
        (a.out / (label + '-argv.json')).write_text(json.dumps(argv, indent=2) + '\n')
        print(label, flush=True)
        with (a.out / (label + '.log')).open('x') as log:
            subprocess.run(argv, check=True, stdout=log, stderr=subprocess.STDOUT, timeout=120)

    raw = bytearray()
    try:
        tool('prior-P4-verify', 'usb_reset', ['verify_flash', '0x20000', str(a.prior)])
        tool('identity-P4-write', 'no_reset', ['write_flash', '--flash_mode', 'keep',
             '--flash_freq', 'keep', '--flash_size', 'keep', '0x20000', str(a.app)])
        tool('identity-P4-verify', 'no_reset', ['verify_flash', '0x20000', str(a.app)])
        reader = serial.Serial(port=None, baudrate=115200, timeout=.2, write_timeout=3)
        reader.dtr = False
        reader.rts = False
        reader.port = str(a.port)
        reader.open()
        HardReset(reader, uses_usb=True)()  # Reset programmer only.
        deadline = time.monotonic() + 30
        with (a.out / 'console.log').open('xb', buffering=0) as log:
            while time.monotonic() < deadline:
                chunk = reader.readline()
                if not chunk:
                    continue
                raw.extend(chunk)
                log.write(chunk)
                line = chunk.decode('ascii', errors='replace').strip()
                print(line, flush=True)
                if any(x in line for x in ('Guru Meditation', 'abort()', 'task_wdt:', 'assert failed')):
                    raise RuntimeError('P4 programmer fault')
                if line == 'READY P4-IDENTITY-ONLY r01 GREEN=46 BLUE=47' and not result['identity_command_sent']:
                    reader.write(b'IDENTIFY\n')
                    reader.flush()
                    result['identity_command_sent'] = True
                m = re.fullmatch(r'IDENTITY ([123]) product=([0-9A-F]{4}) revision=([0-9A-F]{2}) status=([0-9A-F]{2})', line)
                if m:
                    n, product, revision, status = m.groups()
                    result['identities'].append(dict(read=int(n), product=product,
                                                     revision=revision, status=status))
                if line == 'IDENTITY-ONLY DONE; GREEN and BLUE released; MOS untouched':
                    assert [x['read'] for x in result['identities']] == [1, 2, 3]
                    result['proper_product_all_three'] = all(x['product'] == '0007' for x in result['identities'])
                    result['expected_revision_all_three'] = all(x['revision'] == 'AA' for x in result['identities'])
                    result['complete'] = True
                    break
            else:
                raise TimeoutError('Identity-only command did not finish')
    except BaseException as exc:
        result['error'] = repr(exc)
        raise
    finally:
        if reader is not None and reader.is_open:
            reader.close()
        result['elapsed_seconds'] = round(time.monotonic() - started, 3)
        result['console_sha256'] = sha(raw)
        (a.out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
