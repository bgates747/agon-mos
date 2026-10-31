"""Send one fixed RAM-only command to the exactly identified quiet WROOM probe."""
import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import serial
from esptool.reset import HardReset

PORT = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
BANNER = b'WROOM CONSOLE8 HALT RAM PROBE v11 GREEN=GPIO27 BLUE=GPIO26 QUIET'
ROOT = Path(__file__).resolve().parent


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_name', nargs='?', default='probe-001')
    parser.add_argument('--connection-note', default='')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9-]+', args.run_name):
        parser.error('Invalid run name')
    OUT = ROOT / args.run_name
    OUT.mkdir(exist_ok=False)
    result = dict(completed=False, target='Console8', GREEN_clock_GPIO=27,
                  BLUE_data_GPIO=26, series_resistors='Author reports present; last measured33ohms',
                  signal_probes='none', programmer_reset_requested=False,
                  target_reset_requested=False, command_sent=False,
                  operator_connection_note=args.connection_note,
                  operator_authority='Author approves diagnostics at agent discretion after discussion of halt/RAM verification before erase',
                  runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    raw = bytearray()
    h = None
    (OUT / 'runner.py').write_bytes(Path(__file__).read_bytes())
    with (OUT / 'console.bin').open('xb', buffering=0) as log:
        def until(marker, timeout=15):
            data = bytearray()
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                block = h.read(4096)
                if block:
                    data.extend(block); raw.extend(block); log.write(block)
                if marker in data:
                    return bytes(data)
            raise RuntimeError('Timeout waiting for ' + repr(marker))

        try:
            props = subprocess.check_output(['udevadm', 'info', '--query=property', '--name', PORT], text=True)
            (OUT / 'programmer-udev.txt').write_text(props)
            assert 'ID_SERIAL_SHORT=0001\n' in props and 'ID_MODEL=CP2102_USB_to_UART_Bridge_Controller\n' in props
            h = serial.Serial(port=None, baudrate=115200, timeout=.03, exclusive=True)
            h.dtr = False; h.rts = False; h.port = PORT; h.open()
            h.reset_input_buffer()
            result['programmer_reset_requested'] = True
            HardReset(h)()
            boot = until(b'WAIT PROBE CONSOLE8 RAM-ONLY')
            assert BANNER in boot
            pins = re.findall(rb'PINS out=([0-9A-F]+) enable=([0-9A-F]+) in=([0-9A-F]+)', boot)
            assert len(pins) == 1 and int(pins[0][1], 16) & (3 << 26) == 0
            command = b'PROBE CONSOLE8 RAM-ONLY\n'
            assert h.write(command) == len(command)
            h.flush(); result['command_sent'] = True
            data = until(b'PROBE END ', timeout=30)
            if not re.search(rb'PROBE END [^\r\n]+\r?\nPINS [^\r\n]+\r?\n', data):
                data += until(b'BLUE=', timeout=5)
                # Ensure the complete final pin-state line is recorded.
                more = h.read(4096)
                data += more; raw.extend(more); log.write(more)
            ends = re.findall(rb'PROBE END ([^\r\n]+)', data)
            pins = re.findall(rb'PINS out=([0-9A-F]+) enable=([0-9A-F]+) in=([0-9A-F]+) GREEN=(\d) BLUE=(\d)', data)
            assert len(ends) == 1 and len(pins) == 1
            assert int(pins[0][1], 16) & (3 << 26) == 0
            assert b'flash_operations=0' in ends[0]
            statuses = re.findall(rb'HALT STATUS (\d)/3=([0-9A-F]{2}) valid=(\d)', data)
            result.update(completed=True, outcome=ends[0].decode(),
                          passed=ends[0].startswith(b'PASS '),
                          halt_statuses=[dict(trial=int(i), raw=v.decode(), valid=bool(int(ok))) for i,v,ok in statuses],
                          final_state='Both outputs released; serial closed after run',
                          released_levels={'GREEN':int(pins[0][3]), 'BLUE':int(pins[0][4])})
            if result['passed']:
                assert len(statuses) == 3 and all((int(v, 16) & 0xC3) == 0x80 and ok == b'1' for _,v,ok in statuses)
                assert len(re.findall(rb'RAM pattern\d/4 verified twice', data)) == 4
            print(data.decode(errors='replace'), flush=True)
        except BaseException as error:
            result['error'] = repr(error)
            raise
        finally:
            if h is not None and h.is_open:
                h.close()
            result['console_sha256'] = hashlib.sha256(raw).hexdigest()
            (OUT / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
            print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    run()
