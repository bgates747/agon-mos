"""Four-probe ZDI identity capture; no intentional target writes or resets.

Canonical Author-confirmed probe colors, 2026-10-29. Never inherit the
historical BROWN=D3 claim or hard-coded WROOM endpoint names in old decoders.
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

parser = argparse.ArgumentParser()
parser.add_argument('run_name')
parser.add_argument('--compare-clock', action='store_true')
parser.add_argument('--target', choices=['Console8', 'Olimex Agon Light 2'], required=True)
parser.add_argument('--resistor-ohms', type=int, required=True)
parser.add_argument('--firmware-version', type=int, choices=[3, 7, 8], default=7)
parser.add_argument('--clock-strengths', help='Comma-separated levels 0..3; requires v8')
parser.add_argument('--probes', choices=['four', 'target-only', 'target-plus-red', 'none'], default='four')
args = parser.parse_args()
assert re.fullmatch(r'[a-z0-9-]+', args.run_name)
assert args.resistor_ohms > 0
assert not args.compare_clock or args.firmware_version >= 7
strengths = args.clock_strengths.split(',') if args.clock_strengths else None
assert not strengths or (args.firmware_version == 8 and not args.compare_clock
                         and all(x in ('0','1','2','3') for x in strengths))
root = Path(__file__).resolve().parents[2]
out = root / 'build/zdi-qualification-20261030' / args.run_name
out.parent.mkdir(parents=True, exist_ok=True)
out.mkdir(exist_ok=False)
port = '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0'
result = dict(completed=False, target=args.target, target_flash_operations=0,
              target_reset_requested=False, programmer_reset_requested=False,
              operator_statement='Author connected WROOM, sniffer and target to Pi5; confirmed both 33-ohm resistors and all four endpoint probes',
              series_resistor_ohms=args.resistor_ohms,
              probe_map={'D0': f'GREEN: {args.target} GREEN clock, after resistor',
                         'D2': f'BLUE: {args.target} BLUE data, after resistor',
                         'D5': 'RED: WROOM GREEN clock, before resistor',
                         'D7': 'BROWN: WROOM BLUE data, before resistor'},
              canonical_colors={'D0':'GREEN','D1':'YELLOW','D2':'BLUE','D3':'ORANGE',
                                'D4':'PURPLE','D5':'RED','D6':'GRAY','D7':'BROWN'},
              commands=[], captures=[], phases=[], final_state='not opened')
result['probe_setup'] = args.probes
if args.probes == 'target-only':
    result['probe_map']['D5'] = 'RED: disconnected for probe-loading comparison'
    result['probe_map']['D7'] = 'BROWN: disconnected for probe-loading comparison'
    result['operator_statement'] = 'Author confirmed only RED/BROWN probes disconnected; GREEN/BLUE target-end probes, signal wires, 33-ohm resistors and grounds unchanged'
elif args.probes == 'target-plus-red':
    result['probe_map']['D7'] = 'BROWN: disconnected; RED alone reattached on WROOM GREEN clock'
    result['operator_statement'] = 'Author reconnected only RED probe to WROOM-side GREEN clock; BROWN remains disconnected; all signal wiring, resistors, grounds and target-end probes unchanged'
elif args.probes == 'none':
    result['probe_map'] = {key: value.split(':')[0] + ': disconnected; no signal waveform available'
                           for key, value in result['probe_map'].items()}
    result['operator_statement'] = 'Author disconnected all four signal probes only; actual GREEN/BLUE wires, both 33-ohm resistors, grounds and USB unchanged'
    result['capture_limit'] = 'No probes on ZDI signals: analyzer files do not record the link; use software identity/local GPIO results only'
h = None
verified_v7 = False
capture = None
raw = bytearray()
log = (out / 'console.bin').open('xb', buffering=0)


def save():
    result['console_sha256'] = hashlib.sha256(raw).hexdigest()
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')


def start_capture(label, rate, samples):
    global capture
    caplog = (out / (label + '.sigrok.log')).open('x')
    path = out / (label + '.bin')
    capture = subprocess.Popen(['sigrok-cli', '-d', 'fx2lafw', '--config',
                                'samplerate=' + str(rate), '--samples', str(samples),
                                '--output-format', 'binary', '--output-file', str(path)],
                               stdout=caplog, stderr=subprocess.STDOUT)
    caplog.close()
    return path


def finish_capture(path, samples):
    global capture
    capture.wait(timeout=15)
    assert capture.returncode == 0, path.with_suffix('.sigrok.log').read_text()
    assert path.stat().st_size == samples, 'Short capture: ' + str(path)
    result['captures'].append(dict(file=path.name, samples=samples,
                                  samplerate_hz=1000000 if path.name.startswith('passive-') else 24000000,
                                  layout='One uint8 per sample; D0=bit0 through D7=bit7',
                                  sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    capture = None
    save()


def until(marker, timeout=10):
    data = bytearray()
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        block = h.read(4096)
        if block:
            data.extend(block)
            raw.extend(block)
            log.write(block)
        if marker in data:
            return bytes(data)
    raise RuntimeError('Timeout waiting for ' + repr(marker))


def send(command):
    h.write(command.encode('ascii'))
    h.flush()
    result['commands'].append(command)


try:
    # Passive captures first. Cold FX2 firmware loading can re-enumerate USB:
    # allow bounded retries, and send no GPIO command until acquisition works.
    result['host'] = subprocess.check_output(['hostname'], text=True).strip()
    result['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['firmware_expected_banner'] = f'WROOM ZDI IDENTITY ONLY v{args.firmware_version}'
    usb = subprocess.check_output(['lsusb'], text=True)
    (out / 'usb-before.txt').write_text(usb)
    assert '0925:3881' in usb, 'Analyzer is absent; no active test permitted'
    props = subprocess.check_output(['udevadm', 'info', '--query=property', '--name', port], text=True)
    assert 'ID_SERIAL_SHORT=0001\n' in props
    assert 'ID_MODEL=CP2102_USB_to_UART_Bridge_Controller\n' in props
    for attempt in range(1, 4):
        path = start_capture(f'passive-{attempt:03d}', 1000000, 1000000)
        capture.wait(timeout=15)
        if capture.returncode == 0 and path.exists() and path.stat().st_size == 1000000:
            finish_capture(path, 1000000)
            break
        capture = None
        time.sleep(1)
    else:
        raise RuntimeError('No complete passive capture after three attempts; target untouched')
    h = serial.Serial(port=None, baudrate=115200, timeout=.03, exclusive=True)
    h.dtr = False
    h.rts = False
    h.port = port
    h.open()
    h.reset_input_buffer()
    HardReset(h)()  # WROOM only; target reset lead is disconnected.
    result['programmer_reset_requested'] = True
    banner = until(b'READY')
    assert result['firmware_expected_banner'].encode() in banner
    verified_v7 = True
    send('P')
    until(b'READY')
    if strengths:
        send('Z')
        until(b'READY')
    modes = strengths or (['Z', 'A', 'Z', 'A'] if args.compare_clock else ['Z'])
    for index, command in enumerate(modes, 1):
        phase = dict(id=f'FP-{index:03d}', clock_mode='push-pull' if strengths or command == 'Z' else 'open-drain', readings=[])
        if strengths:
            phase['clock_drive_level'] = int(command)
        result['phases'].append(phase)
        path = start_capture(phase['id'], 24000000, 96000000)
        ready_deadline = time.monotonic() + 1.5
        while time.monotonic() < ready_deadline:
            assert capture.poll() is None, 'Capture exited before pin commands'
            if path.exists() and path.stat().st_size > 0:
                break
            time.sleep(.05)
        else:
            raise RuntimeError('No positive capture-file growth; no active pin commands permitted')
        if args.firmware_version >= 7:
            send(command)
            state = until(b'READY')
        else:
            state = b''  # v3 has no Z/A handler; its clock is baseline push-pull.
        if strengths:
            expected = f'CLOCK DRIVE requested={command} actual={command} data_before=2 data_after=2 errors=0,0,0,0'
            assert expected.encode() in state, 'Drive setting or unchanged DATA check failed'
        elif args.firmware_version >= 7:
            assert ('GREEN mode=' + phase['clock_mode']).encode() in state
        for trial in range(1, 6):
            assert capture.poll() is None, 'Capture ended before identity trial'
            send('T')
            data = until(b'READY')
            matches = re.findall(rb'READ settling_us=10 raw=([0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2} [0-9A-F]{2}) id=([0-9A-F]{4}) rev=([0-9A-F]{2})', data)
            assert len(matches) == 1
            values, product, revision = matches[0]
            traces = re.findall(rb'TX(\d\d) desired=(\d) out=(\d) en=(\d) in=(\d)', data)
            assert len(traces) == 13
            reading = dict(trial=trial, raw=values.decode(), product=product.decode(),
                           revision=revision.decode(), valid=product == b'0007' and revision == b'AA',
                           tx=[dict(index=int(i), desired=int(d), out=int(o), enable=int(e), input=int(p)) for i,d,o,e,p in traces])
            phase['readings'].append(reading)
            print(phase['id'], trial, reading['raw'], 'valid=' + str(reading['valid']), flush=True)
            time.sleep(.1)
        send('Q')
        until(b'QUIET - both released')
        finish_capture(path, 96000000)
        phase['valid_count'] = sum(r['valid'] for r in phase['readings'])
    result['completed'] = True
except BaseException as error:
    result['error'] = repr(error)
    raise
finally:
    if h is not None and h.is_open and verified_v7:
        try:
            if strengths:
                send('2')
                assert b'actual=2 data_before=2 data_after=2 errors=0,0,0,0' in until(b'READY')
            if args.firmware_version >= 7:
                send('Z')
                until(b'READY')
            send('Q')
            until(b'QUIET - both released')
            send('P')
            status = until(b'READY')
            rows = re.findall(rb'PINS out=([0-9A-F]+) enable=([0-9A-F]+) in=([0-9A-F]+)', status)
            assert rows
            latch, enabled, inputs = (int(x, 16) for x in rows[-1])
            assert (enabled & (3 << 26)) == 0
            result['final_state'] = 'Both GPIO outputs released; GREEN clock push-pull restored, BLUE mode unchanged'
            if strengths:
                result['final_state'] += '; CLOCK drive level2 restored, DATA remains level2'
            result['released_levels'] = {'GREEN': (inputs >> 26) & 1, 'BLUE': (inputs >> 27) & 1}
        except BaseException as error:
            result['cleanup_error'] = repr(error)
            result['final_state'] = 'Release not verified'
            result['completed'] = False
    if h is not None and h.is_open:
        h.close()
    if capture is not None and capture.poll() is None:
        capture.terminate()
        capture.wait(timeout=10)
    log.close()
    save()
    print(json.dumps({k: v for k,v in result.items() if k != 'phases'}, indent=2), flush=True)
