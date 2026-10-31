"""Canonical shared reservations remain consistent without an installed SDK."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
API = ROOT / 'src/shared-api'


class SharedBindingTests(unittest.TestCase):
    def test_uart_and_retired_allocations(self):
        data = json.loads((API / 'api/reservations.json').read_text())
        entries = {(r['namespace'], r['value']): r for r in data['reservations']}
        self.assertEqual(len(entries), len(data['reservations']))
        self.assertEqual(entries[('mos_getfunction', 19)]['owner'], 'agon-mos')
        self.assertEqual(entries[('mos_getfunction', 19)]['abi']['minimum_table_bytes'], 54)
        self.assertEqual(entries[('mos_getfunction', 18)]['status'], 'retired')

    def test_bindings_have_same_value_and_registry_identity(self):
        raw = (API / 'api/reservations.json').read_bytes()
        asm = (API / 'src/mos_api_reservations.inc').read_text()
        c = (API / 'api/include/mos_api_reservations.h').read_text()
        self.assertIn('.equiv mos_function_uart0_async, 0x13', asm)
        self.assertIn('#define MOS_FUNCTION_UART0_ASYNC 0x13u', c)
        self.assertIn(hashlib.sha256(raw).hexdigest(), c)
        self.assertNotIn('qsort', asm.lower())
        self.assertNotIn('qsort', c.lower())

    def test_canonical_entrypoints_import_shared_bindings(self):
        self.assertIn('.include "mos_api_reservations.inc"', (API / 'src/mos_api.inc').read_text())
        header = (API / 'api/include/agon/mos.h').read_text()
        self.assertIn('#include_next <agon/mos.h>', header)
        self.assertIn('#include "../mos_api_reservations.h"', header)


if __name__ == '__main__': unittest.main()
