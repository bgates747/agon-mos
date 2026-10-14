"""One-shot counterfactual in a captured, owned stalled emulator only.

This changes guest UART2 INT_ENA through the existing MMIO path. It is a
diagnostic intervention, never a runtime repair or a qualification run.
"""
import hashlib
import json
import os
from pathlib import Path
import gdb

dest = Path(os.environ['UART_AB_CAPTURE'])
analysis = json.loads((dest/'analysis.json').read_text())
assert analysis['receive_wakeup_failure'] is True
assert hashlib.sha256(Path(f'/proc/{gdb.selected_inferior().pid}/exe').read_bytes()).hexdigest() == '412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'
session = (dest/'adapter-session-state.bin').read_bytes()
memory = int.from_bytes(session[0xe140:0xe148],'little')
previous = int(analysis['vdp_uart2']['int_ena'],16)
assert previous&0x101 == 0
value = previous|0x101
command = f'call (void)mem_write32_slow((void*){memory}, 0x3ff6e00c, {value})'
(dest/'diagnostic-intervention.json').write_text(json.dumps(dict(
    qualification=False,action='One UART2 INT_ENA MMIO write',previous=hex(previous),
    value=hex(value),command=command),indent=2)+'\n')
gdb.execute(command)
