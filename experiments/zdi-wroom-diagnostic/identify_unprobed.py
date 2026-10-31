"""Bounded pin-specific ZDI identity checks without analyzer connections.

Reset only the WROOM programmer. Send P/T/Q only after checking its quiet v3
banner; no target programming, memory access, halt or reset commands exist here.
The target and physical setup are operator attestations, not USB identification.
"""
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
BANNER = b'WROOM ZDI IDENTITY ONLY v3 - GPIO26=TCK GPIO27=TDI'


def parse_read(data):
    rows = re.findall(rb'READ settling_us=10 raw=([0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}) id=([0-9A-F]{4}) rev=([0-9A-F]{2})', data)
    if len(rows) != 1:
        raise RuntimeError('Expected exactly one slow identity reply')
    values, product, revision = rows[0]
    octets = bytes.fromhex(values.decode())
    if product.decode() != f'{int.from_bytes(octets[:2], "little"):04X}' or int(revision, 16) != octets[2]:
        raise RuntimeError('Reply fields disagree')
    traces = re.findall(rb'TX(\d\d) desired=(\d) out=(\d) en=(\d) in=(\d)', data)
    if len(traces) != 13 or [int(row[0]) for row in traces] != list(range(13)):
        raise RuntimeError('Incomplete or unordered driven-bit snapshots')
    # Snapshots encode GPIO26/27 as a two-bit field: CLOCK is held LOW,
    # DATA occupies bit1, and both output enables are set.
    source_ok = all(int(o) == int(p) == (int(d) << 1) and int(e) == 3
                    for _, d, o, e, p in traces)
    return dict(raw=values.decode(), product=product.decode(), revision=revision.decode(),
                status=f'{octets[3]:02X}', valid=octets[:3] == b'\x07\x00\xAA',
                exact_0700AA1C=octets == b'\x07\x00\xAA\x1C',
                local_drive_checks_pass=source_ok,
                tx=[dict(index=int(i), desired=int(d), out=int(o), enable=int(e), input=int(p))
                    for i, d, o, e, p in traces])


def parse_released(data, clock_pin=26, data_pin=None):
    if data_pin is None:
        data_pin = clock_pin + 1
    rows = re.findall(rb'PINS out=([0-9A-F]+) enable=([0-9A-F]+) in=([0-9A-F]+)', data)
    if len(rows) != 1:
        raise RuntimeError('Expected exactly one pin-status reply')
    latch, enabled, inputs = (int(x, 16) for x in rows[0])
    if enabled & ((1 << clock_pin) | (1 << data_pin)):
        raise RuntimeError('GREEN/BLUE output enable remains set')
    return dict(output_latch=f'{latch:08X}', output_enable=f'{enabled:08X}',
                input_register=f'{inputs:08X}', GREEN=(inputs >> clock_pin) & 1,
                BLUE=(inputs >> data_pin) & 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_name')
    parser.add_argument('--target', choices=['Console8', 'Olimex Agon Light 2', 'unconfirmed Agon'], required=True)
    parser.add_argument('--connection-note', required=True)
    parser.add_argument('--sets', type=int, choices=range(1, 5), default=4)
    parser.add_argument('--resistor-ohms', type=int, default=33)
    parser.add_argument('--probe-state', choices=['none', 'attached-unspecified', 'unknown'],
                        default='none', help='Record actual reported signal-probe state; this runner takes no waveform')
    parser.add_argument('--pins', choices=['26-27', '18-19', '27-26'], default='26-27',
                        help='CLOCK-DATA mapping: require matching v3, v9 or v10 banner')
    parser.add_argument('--repeat-invalid', action='store_true',
                        help='Complete one five-read set despite invalid identities; still stop on local drive failure')
    args = parser.parse_args()
    clock_pin, data_pin = (int(p) for p in args.pins.split('-'))
    expected_banner = {'26-27': BANNER,
                       '18-19': b'WROOM ZDI IDENTITY ONLY v9 - GPIO18=TCK GPIO19=TDI',
                       '27-26': b'WROOM ZDI IDENTITY ONLY v10 - GPIO27=TCK GPIO26=TDI'}[args.pins]
    if args.repeat_invalid and args.sets != 1:
        parser.error('--repeat-invalid requires --sets 1')
    if not re.fullmatch(r'[a-z0-9-]+', args.run_name) or args.resistor_ohms < 0:
        parser.error('Invalid run name or resistor value')
    out = Path(__file__).resolve().parents[2] / 'build/zdi-unprobed-20261030' / args.run_name
    out.mkdir(parents=True, exist_ok=False)
    result = dict(completed=False, target=args.target, operator_connection_note=args.connection_note,
                  series_resistor_ohms=args.resistor_ohms, signal_probes=args.probe_state,
                  waveform_available=False, target_reset_requested=False,
                  target_flash_operations=0, target_memory_operations=0,
                  target_halt_requested=False, programmer_resets_requested=0,
                  expected_programmer_banner=expected_banner.decode(),
                  GREEN_clock_GPIO=clock_pin, BLUE_data_GPIO=data_pin,
                  runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  host=subprocess.check_output(['hostname'], text=True).strip(),
                  commands=[], sets=[], final_state='not opened')
    result['continue_after_invalid_identity'] = args.repeat_invalid
    (out / 'runner.py').write_bytes(Path(__file__).read_bytes())
    raw = bytearray()
    handle = None
    verified = False
    with (out / 'console.bin').open('xb', buffering=0) as log:
        def save():
            result['console_sha256'] = hashlib.sha256(raw).hexdigest()
            (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')

        def until(marker, timeout=10):
            data = bytearray()
            end = time.monotonic() + timeout
            while time.monotonic() < end:
                block = handle.read(4096)
                if block:
                    data.extend(block)
                    raw.extend(block)
                    log.write(block)
                if marker in data:
                    return bytes(data)
            raise RuntimeError('Timeout waiting for ' + repr(marker))

        def send(command):
            if not verified or command not in ('P', 'T', 'Q'):
                raise RuntimeError('Unverified programmer or unpermitted command')
            if handle.write(command.encode()) != 1:
                raise RuntimeError('Incomplete serial command write')
            handle.flush()
            result['commands'].append(command)

        def release():
            send('Q')
            until(b'QUIET - both released')
            send('P')
            result['released_pins'] = parse_released(until(b'READY'), clock_pin, data_pin)
            result['final_state'] = 'Both GPIO outputs released; serial closed after run'

        try:
            for name, command in [('usb.txt', ['lsusb']), ('usb-topology.txt', ['lsusb', '-t']),
                                  ('programmer-udev.txt', ['udevadm', 'info', '--query=property', '--name', PORT])]:
                (out / name).write_text(subprocess.check_output(command, text=True))
            props = (out / 'programmer-udev.txt').read_text().splitlines()
            if 'ID_SERIAL_SHORT=0001' not in props or 'ID_MODEL=CP2102_USB_to_UART_Bridge_Controller' not in props:
                raise RuntimeError('WROOM USB identity mismatch')
            handle = serial.Serial(port=None, baudrate=115200, timeout=.03, exclusive=True)
            handle.dtr = False
            handle.rts = False
            handle.port = PORT
            handle.open()
            stopped = False
            for set_index in range(1, args.sets + 1):
                verified = False
                handle.reset_input_buffer()
                result['programmer_resets_requested'] += 1
                HardReset(handle)()  # WROOM only; no target RESET connection.
                boot = until(b'READY')
                if expected_banner not in boot or b'QUIET - pins released with pull-ups' not in boot:
                    raise RuntimeError('Expected quiet pin-specific boot not received; no command sent')
                verified = True
                send('P')
                parse_released(until(b'READY'), clock_pin, data_pin)
                phase = dict(set=set_index, readings=[])
                result['sets'].append(phase)
                for trial in range(1, 6):
                    send('T')
                    reading = parse_read(until(b'READY'))
                    reading['trial'] = trial
                    phase['readings'].append(reading)
                    print(f'set{set_index} trial{trial}: {reading["raw"]} valid={reading["valid"]} local={reading["local_drive_checks_pass"]}', flush=True)
                    save()
                    if (not reading['local_drive_checks_pass'] or
                            (not reading['valid'] and not args.repeat_invalid)):
                        result['stopped_on_bad_read'] = True
                        stopped = True
                        break
                    time.sleep(.1)
                release()
                if stopped:
                    break
            result['completed'] = True
        except BaseException as error:
            result['error'] = repr(error)
            raise
        finally:
            if handle is not None and handle.is_open:
                if verified:
                    try:
                        release()
                    except BaseException as error:
                        result['cleanup_error'] = repr(error)
                        result['completed'] = False
                        result['final_state'] = 'Pin release not verified'
                handle.close()
            readings = [r for s in result['sets'] for r in s['readings']]
            result['read_count'] = len(readings)
            result['valid_count'] = sum(r['valid'] for r in readings)
            result['exact_count'] = sum(r['exact_0700AA1C'] for r in readings)
            save()
            print(json.dumps({k: v for k, v in result.items() if k != 'sets'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
