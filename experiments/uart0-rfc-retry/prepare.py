#!/usr/bin/env python3
"""Reconstruct a private RC3 pair and minimal CTS patch; no build/device calls."""
from pathlib import Path
import argparse, difflib, hashlib, io, json, subprocess, tarfile

PIN = '97311c437093e416342a6c836cf9914f2ced027d'

def source(repo, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', f'{PIN}:{path}']).decode().replace('\r\n', '\n')

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f'Pinned donor seam changed: {old[:70]!r}')
    return text.replace(old, new, 1)

def candidate(serial, irq):
    serial = replace_once(serial, '\t\t \tXDEF\tfill_uart0_tx_fifo\n',
        '\t\t \tXDEF\tfill_uart0_tx_fifo\n'
        '\t\t\tXDEF\tuart0_async_retry, uart0_tx_retry_pending\n')
    begin = serial.index('\t\t\t.macro WAIT_CTS\n')
    end = serial.index('\t\t\t.endm\n', begin) + len('\t\t\t.endm\n')
    serial = serial[:begin] + serial[end:]
    serial = replace_once(serial, 'uart0_async_send:\n',
        'uart0_async_send:\n\t\t\txor a\n\t\t\tld (uart0_tx_retry_pending),a\n')
    serial = replace_once(serial, 'fill_uart0_tx_fifo:\n',
        'fill_uart0_tx_fifo:\n'
        '\t\t\t; Admit before changing remaining count or source.\n'
        '\t\t\tin0 a,(PD_DR)\n\t\t\ttst a,8\n'
        '\t\t\tjr nz,uart0_tx_defer\n')
    if serial.count('\t\t\tWAIT_CTS\n') != 2:
        raise ValueError('Expected two donor waits')
    serial = serial.replace('\t\t\tWAIT_CTS\n', '')
    serial = replace_once(serial, '\t\t\tcall uart0_tx_callback\n',
        '\t\t\txor a\n\t\t\tld (uart0_tx_retry_pending),a\n'
        '\t\t\tcall uart0_tx_callback\n')
    serial += '''
; Only AF has been stacked by the common UART0 handler on this path.
uart0_tx_defer:
            in0 a,(UART0_IER)
            and 0xfd
            out0 (UART0_IER),a
            ld a,1
            ld (uart0_tx_retry_pending),a
            pop af
            ei
            reti.lil

; Called under existing VBlank exclusion/saves. No UART I/O while inactive.
; Rearm only: the UART0 interrupt retains sole ownership of FIFO copying.
uart0_async_retry:
            ld a,(uart0_tx_retry_pending)
            or a
            ret z
            in0 a,(PD_DR)
            tst a,8
            ret nz
            xor a
            ld (uart0_tx_retry_pending),a
            in0 a,(UART0_IER)
            or 2
            out0 (UART0_IER),a
            ret

.bss
uart0_tx_retry_pending: .ds 1
'''
    irq = replace_once(irq, '\t\t\tXREF\tfill_uart0_tx_fifo\n',
        '\t\t\tXREF\tfill_uart0_tx_fifo\n\t\t\tXREF\tuart0_async_retry\n')
    irq = replace_once(irq, '\t\t\tLD\t\t(_clock + 3), A\t\t\t\n',
        '\t\t\tLD\t\t(_clock + 3), A\t\t\t\n'
        '\t\t\tCALL\tuart0_async_retry\n')
    return serial, irq

def prepare(repo, output):
    output.mkdir(parents=True, exist_ok=False)
    blob = subprocess.check_output(['git', '-C', str(repo), 'archive', PIN,
        'Makefile', 'makefile.inc', 'linker.conf', 'src', 'src_fatfs', 'src_umm_malloc'])
    for label in ('original', 'candidate'):
        root = output / label
        root.mkdir()
        with tarfile.open(fileobj=io.BytesIO(blob)) as arc:
            arc.extractall(root, filter='data')
    inputs = {p: source(repo, p) for p in ('src/serial.asm', 'src/interrupts.asm')}
    outputs = dict(zip(inputs, candidate(*inputs.values())))
    patch = ''
    for p in inputs:
        # Both snapshots normalize CRLF for a portable review/apply patch.
        (output/'original'/p).write_text(inputs[p])
        (output/'candidate'/p).write_text(outputs[p])
        patch += ''.join(difflib.unified_diff(inputs[p].splitlines(True),
            outputs[p].splitlines(True), fromfile='a/'+p, tofile='b/'+p))
    (output/'bounded-cts.patch').write_text(patch)
    manifest = {'donor': PIN, 'source': str(repo), 'scope': 'private original/candidate; no install',
        'files': {p: {'original': hashlib.sha256(inputs[p].encode()).hexdigest(),
                      'candidate': hashlib.sha256(outputs[p].encode()).hexdigest()} for p in inputs}}
    (output/'source.json').write_text(json.dumps(manifest, indent=2)+'\n')
    return manifest

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--donor',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    print(json.dumps(prepare(a.donor,a.output),indent=2))
