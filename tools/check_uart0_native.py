#!/usr/bin/env python3
"""Fail-closed UART contracts on the actual root firmware-check ELF.

Inspect bytes/symbols rather than trusting source spelling or the known broken
backward-JR rendering in Binutils. Behavioral/CTS/lifetime tests are separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess


def elf_image(path):
    raw = path.read_bytes()
    head = struct.unpack_from('<16sHHIIIIIHHHHHH', raw)
    assert head[0][:6] == b'\x7fELF\x01\x01', 'Expected little-endian ELF32'
    memory = {}
    for i in range(head[10]):
        kind, offset, va, pa, size, memsize, flags, align = struct.unpack_from(
            '<8I', raw, head[5] + i * head[9])
        if kind == 1:
            for n, value in enumerate(raw[offset:offset+size]):
                address = pa+n
                assert address not in memory or memory[address] == value
                memory[address] = value
    return memory


def check(source, elf, nm):
    memory = elf_image(elf)
    symbols = {}
    for line in subprocess.check_output([str(nm), '-a', str(elf)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 3:
            try:
                symbols[parts[2]] = int(parts[0], 16)
            except ValueError:
                pass
    def address(name):
        assert name in symbols, 'Missing symbol: '+name
        return symbols[name]
    def read(at, size):
        assert all(at+n in memory for n in range(size)), ('Unmapped ROM', hex(at), size)
        return bytes(memory[at+n] for n in range(size))
    def code(name, size):
        return read(address(name), size)
    def operand(name):
        return address(name).to_bytes(3, 'little')
    def starts_call(entry, target):
        assert code(entry, 4) == b'\xcd'+operand(target), (entry, target)
    def calls(entry, length, target, count=1):
        assert code(entry, length).count(b'\xcd'+operand(target)) >= count, (entry, target)
    api_root = (source / 'src/shared-api').resolve(strict=True)
    lock = json.loads((source/'dependencies.json').read_text())
    for name,pin in lock['api_files'].items():
        assert hashlib.sha256((api_root/name).read_bytes()).hexdigest() == pin, name
    registry = api_root / 'api/reservations.json'
    assert hashlib.sha256(registry.read_bytes()).hexdigest() == '12a683216ccf2a522e9eaf3ac95f1dcf1584a57e9908e40b9e375f6217f8d6f6'
    for name in ('mos_api.inc', 'mos_api_reservations.inc'):
        selected = source / 'src' / name
        assert not selected.is_symlink()
        assert selected.read_text().splitlines()[-1] == '.include "src/shared-api/src/'+name+'"'
        assert (api_root/'src'/name).is_file()
    assert (source / 'api').resolve() == api_root / 'api'
    register = json.loads(registry.read_text())
    allocations = {r['value']:r for r in register['reservations']}
    slot = next(v for v,r in allocations.items() if r.get('asm_symbol') == 'mos_function_uart0_async')
    assert slot == address('mos_function_uart0_async') == 19
    assert allocations[18]['status'] == 'retired'
    assert address('mos_function_block_size') == 20
    table = address('mos_function_block_start')
    assert read(table+18*3,3) == bytes(3), 'Retired slot12 must remain null'
    assert read(table+slot*3,3) == operand('uart0_async_getapi')
    assert 'mos_function_qsort' not in symbols
    # getfunction13 returns this function; the function returns the UTX1 table.
    assert code('uart0_async_getapi',6) == b'\x21'+operand('uart0_async_api')+b'\xaf\xc9'
    api = read(address('uart0_async_api'),54)
    assert address('uart0_async_api_end')-address('uart0_async_api') == 54
    assert api[:13] == b'UTX1\x01\x02\x36\x0f\x03\x10\xff\xff\x00', 'Invalid UTX1 header'
    targets = ['tx_open','tx_reserve','tx_publish','tx_status','tx_cancel','tx_reap',
               'tx_poll_drain','tx_close','tx_kick','tx_rx_errors','tx_diag_take',
               'tx_set_cts_batch','tx_get_cts_batch']
    for n,name in enumerate(targets):
        assert api[13+n*3:16+n*3] == operand(name), name
    assert api[52:] == b'\x8b\x80'
    offsets = dict(tx_slots=0,tx_head=57,tx_tail=60,tx_next_ticket=63,tx_tmp=66,
        tx_opened=69,tx_barrier=70,tx_in_isr=71,tx_saved_ier=72,tx_ier=73,
        tx_rx_errors=74,tx_modem_deltas=75,tx_cause_budget=76,tx_rx_budget=77,
        tx_tx_serviced=78,tx_unknown_cause=79,tx_cts_batch=80,tx_block_budget=81,
        tx_block_count=82,uart0_sync_depth=85)
    start = address('tx_slots')
    for name,offset in offsets.items():
        assert address(name) == start+offset, (name, offset)
    assert 0xbc000 <= start <= 0xc0000-86 and address('STRIDE') == 19
    assert address('UART0_PRODUCTION') == 1 and address('UART0_BATCH_SCALAR') == 0
    batch = read(address('batch_count'),address('batch_more')-address('batch_count'))
    assert batch.count(b'\xed\xc3') == 1, 'Missing/ambiguous native OTIRX'
    assert b'\x11\xc0\x00\x00\xed\xc3' in batch, 'OTIRX needs fixed UART port DE'
    assert code('service_batch',2) == b'\x3e\x10', 'Refill budget must be16'
    starts_call('batch_next','read_msr')
    assert code('_uart0_handler',4) == b'\xc3'+operand('tx_isr')
    starts_call('mos_api_oscli','uart0_return_fence')
    starts_call('mos_api_setkbvector','uart0_return_fence')
    starts_call('_execSM','uart0_return_fence')
    calls('_execSM',12,'uart0_return_fence',2)
    starts_call('_rst_18_handler','uart0_sync_begin')
    starts_call('_rst_18_done','uart0_sync_end')
    starts_call('UART0_wait_CTS','uart0_read_msr')
    starts_call('UART0_serial_TX1','uart0_read_lsr')
    starts_call('UART0_serial_RX','uart0_read_lsr')
    calls('_on_crash',96,'uart0_return_fence')
    init = code('_uart0_tx_init',15)
    assert init.startswith(b'\x21\x01\x00\x00\x22'+operand('tx_next_ticket'))
    assert b'\x3e\x01\x32'+operand('tx_cts_batch') in init, 'Default must be1'
    main = code('_main',256)
    assert main.index(b'\xcd'+operand('_uart0_tx_init')) < main.index(b'\xcd'+operand('_init_interrupts'))
    # N-007: native int/UINT24 multiplication wrapped at the VDP boot rate.
    # For this pinned Clang/SDK, a 32-bit multiply-by-16 uses __lshl;
    # the withdrawn image used __ishl and programmed divisor11 instead of1.
    # Execute the linked routines with boot_audit.rs as a separate register test.
    for entry, end in (('_open_UART0', '_open_UART1'),
                       ('_open_UART1', '_close_UART1')):
        routine = code(entry, address(end)-address(entry))
        assert b'\xcd'+operand('__lshl') in routine, entry+' lacks 32-bit baud multiplication'
        assert b'\xcd'+operand('__ishl') not in routine, entry+' uses overflowing 24-bit baud multiplication'
        assert b'\xcd'+operand('__ldivu') in routine, entry+' lacks 32-bit baud division'
    assert address('__vector_table') == 0x100
    assert address('__stack')-address('__stack_bottom') == 2048
    return dict(passed=True, ABI='1.2', discovery_slot=slot, retired_slot_null=True,
                table_bytes=54, callable_operations=12, data_pointers=1,
                UART_BSS_bytes=86, slots=3, stride=19, OTIRX_opcode='ED C3',
                refill_cap=16, default_batch=1, canonical_API_sha256=hashlib.sha256(registry.read_bytes()).hexdigest(),
                UART_baud_multiply_32bit=True,
                checked_elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),
                behavioral_qualification_separate=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--elf',type=Path,required=True)
    p.add_argument('--nm',type=Path,required=True)
    p.add_argument('--objdump',type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(check(args.source.resolve(),args.elf.resolve(),args.nm.resolve()),indent=2))
