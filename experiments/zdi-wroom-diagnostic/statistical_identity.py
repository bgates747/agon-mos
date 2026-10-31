#!/usr/bin/env python3
"""Repeated read-only identity requests using the preserved WROOM v3 image."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time

import serial
from esptool.reset import HardReset
from identify_unprobed import BANNER, PORT, parse_read, parse_released


def wilson(successes, trials):
    z = 1.959963984540054
    rate = successes / trials
    scale = 1 + z * z / trials
    center = (rate + z * z / (2 * trials)) / scale
    half = z * math.sqrt(rate * (1 - rate) / trials + z * z / (4 * trials * trials)) / scale
    return [max(0, center - half), min(1, center + half)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--target', choices=('Console8', 'Olimex Agon Light 2'), required=True)
    p.add_argument('--resistor-ohms', type=int, required=True)
    p.add_argument('--connection-note', required=True)
    p.add_argument('--ground-zdi-pin', type=int, choices=(3, 5), required=True)
    p.add_argument('--clock-color', choices=('BLUE', 'GREEN'), default='BLUE')
    p.add_argument('--data-color', choices=('BLUE', 'GREEN'), default='GREEN')
    a = p.parse_args()
    if a.resistor_ohms < 0 or a.clock_color == a.data_color:
        p.error('Invalid resistor value or duplicate wire colors')
    a.out.mkdir(parents=True, exist_ok=False)
    props = subprocess.check_output(['udevadm', 'info', '--query=property', '--name', PORT], text=True)
    assert 'ID_SERIAL_SHORT=0001\n' in props and 'ID_MODEL=CP2102_USB_to_UART_Bridge_Controller\n' in props
    (a.out / 'programmer-udev.txt').write_text(props)
    result = dict(target=a.target, host=subprocess.check_output(['hostname'], text=True).strip(),
                  clock_GPIO=26, data_GPIO=27, clock_wire_color=a.clock_color,
                  data_wire_color=a.data_color, series_resistors_ohm=a.resistor_ohms,
                  ground_zdi_pin=a.ground_zdi_pin, operator_change=a.connection_note,
                  firmware='preserved identity-only v3', firmware_sha256='abaa0bc98876389f14a2f92a47115a5e95a5009dd1975f61a026d74978984fd9',
                  command='S', edge_settling_us=10, per_firmware_read_gap_ms=50,
                  target_reset_requested=False, target_halt_requested=False,
                  target_memory_operations=0, target_flash_operations=0,
                  intended_reads=1000, intended_programmer_epochs=10, sessions=[],
                  signal_probes='No analyzer added by agent; no capture', completed=False,
                  independence_limit='Repeated requests on one setup may be correlated; binomial intervals are conditional on independent stationary trials.')
    raw = bytearray()
    started = time.monotonic()
    h = None
    verified = False
    with (a.out / 'console.bin').open('xb', buffering=0) as log:
        def save():
            result['elapsed_seconds'] = round(time.monotonic() - started, 3)
            result['console_sha256'] = hashlib.sha256(raw).hexdigest()
            (a.out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')

        def until(marker, seconds=10):
            chunk = bytearray()
            deadline = time.monotonic() + seconds
            while time.monotonic() < deadline:
                b = h.read(4096)
                if b:
                    raw.extend(b)
                    chunk.extend(b)
                    log.write(b)
                if marker in chunk:
                    return bytes(chunk)
            raise TimeoutError('Timeout waiting for ' + repr(marker))

        def send(command):
            assert verified and command in ('P', 'Q', 'S')
            assert h.write(command.encode()) == 1
            h.flush()

        def release():
            send('Q')
            until(b'QUIET - both released')
            send('P')
            # The historical parser's GREEN/BLUE keys mean GPIO26/27, not
            # the Author's subsequently changed physical insulation colors.
            state = parse_released(until(b'READY'))
            clock = state.pop('GREEN')
            data = state.pop('BLUE')
            state.update(clock_input=clock, data_input=data)
            state[a.clock_color] = clock
            state[a.data_color] = data
            return state

        try:
            h = serial.Serial(port=None, baudrate=115200, timeout=.03, write_timeout=3, exclusive=True)
            h.dtr = False
            h.rts = False
            h.port = PORT
            h.open()
            for session in range(1, 11):
                verified = False
                h.reset_input_buffer()
                HardReset(h)()  # Programmer only; never open mainboard serial/reset.
                boot = until(b'READY')
                assert BANNER in boot and b'QUIET - pins released with pull-ups' in boot
                verified = True
                send('P')
                parse_released(until(b'READY'))
                phase = dict(session=session, readings=[])
                result['sessions'].append(phase)
                for block in range(1, 11):
                    send('S')
                    reply = until(b'READY', seconds=15)
                    segments = reply.split(b'READ settling_us=')[1:]
                    assert len(segments) == 10, 'Incomplete ten-read block'
                    for index, segment in enumerate(segments, 1):
                        row = parse_read(b'READ settling_us=' + segment)
                        row.update(block=block, index_in_block=index,
                                   index_in_session=len(phase['readings']) + 1)
                        phase['readings'].append(row)
                    save()
                phase['released_pins'] = release()
                rows = [r for s in result['sessions'] for r in s['readings']]
                print(f'{len(rows)}/1000: identity correct={sum(r["valid"] for r in rows)}, '
                      f'exact status={sum(r["exact_0700AA1C"] for r in rows)}, '
                      f'local drive mismatches={sum(not r["local_drive_checks_pass"] for r in rows)}', flush=True)
                save()
            result['completed'] = True
        except BaseException as exc:
            result['error'] = repr(exc)
            raise
        finally:
            if h is not None and h.is_open:
                if verified:
                    try:
                        result['final_released_pins'] = release()
                    except BaseException as exc:
                        result['cleanup_error'] = repr(exc)
                h.close()
            rows = [r for s in result['sessions'] for r in s['readings']]
            result['read_count'] = len(rows)
            if rows:
                good = sum(r['valid'] for r in rows)
                result.update(valid_identity_count=good, invalid_identity_count=len(rows)-good,
                              exact_0700AA1C_count=sum(r['exact_0700AA1C'] for r in rows),
                              local_drive_failure_reads=sum(not r['local_drive_checks_pass'] for r in rows),
                              success_fraction=good/len(rows),
                              success_wilson_95=wilson(good, len(rows)),
                              reply_histogram=dict(Counter(r['raw'] for r in rows)),
                              first_after_reset_valid=sum(s['readings'][0]['valid'] for s in result['sessions'] if s['readings']),
                              first_after_reset_total=sum(bool(s['readings']) for s in result['sessions']))
                if good == len(rows):
                    result['zero_failures_one_sided_95_failure_upper_bound'] = -math.expm1(math.log(.05)/len(rows))
                (a.out / 'readings.json').write_text(json.dumps(rows, indent=2) + '\n')
            save()
            print(json.dumps({k:v for k,v in result.items() if k!='sessions'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
