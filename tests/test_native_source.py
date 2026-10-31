"""Source/ancestry/traceability checks that need no emulator or proprietary SDK."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class NativeSourceTests(unittest.TestCase):
    def test_official_history_is_retained(self):
        result=subprocess.run(['git','merge-base','--is-ancestor',
            '8336409351ee5314e02801a7b72a4f1bb5282519','HEAD'],cwd=ROOT)
        self.assertEqual(result.returncode,0)

    def test_initial_map_and_current_source_are_readable(self):
        mapping=json.loads((ROOT/'docs/migration/initial-map.json').read_text())
        self.assertEqual(len(mapping['files']),20)
        for entry in mapping['files']:
            path=ROOT/entry['native_path'];text=path.read_text()
            original=subprocess.check_output(['git','show',mapping['upstream_commit']+':'+entry['upstream_path']],cwd=ROOT)
            self.assertEqual(hashlib.sha256(original).hexdigest(),entry['upstream_sha256'])
            self.assertRegex(entry['native_sha256'],r'^[0-9a-f]{64}$')
            self.assertTrue(all(n is None or 1<=n<=len(original.splitlines()) for n in entry['upstream_line_map']))
            self.assertNotIn('.Lzds_',text)
            self.assertNotIn('DO NOT EDIT: generated',text)
            self.assertIn(entry['upstream_path'],text.splitlines()[0])

    def test_macros_are_maintained_not_expanded(self):
        macros=(ROOT/'src/macros.inc').read_text()
        self.assertIn('.macro TIMER_WAIT',macros)
        self.assertIn('.LTIMER_WAIT_loop\\@',macros)
        self.assertIn('TIMER_EXP',macros)
        self.assertNotIn('TIMER_EXP?',macros)
        self.assertIn('DELAY_MS',(ROOT/'src/sd.asm').read_text())

    def test_native_build_never_invokes_conversion(self):
        make=(ROOT/'Makefile').read_text()
        self.assertIn('projects/native-foundation/build.py',make)
        self.assertNotIn('migrate.py',make)
        self.assertNotIn('prepare_mos_worktree',make)
        self.assertNotIn('zds2gas',make)

    def test_uart_profile_preserves_native_foundation_inventory(self):
        profile=json.loads((ROOT/'build.json').read_text())
        self.assertEqual(len(profile['c_sources']),16)
        self.assertEqual(len(profile['asm_sources']),16)
        self.assertEqual(profile['asm_sources'][-1], 'src/uart0_async.asm')
        self.assertEqual(profile['c_overrides'],{'src_fatfs/ff.c':'-Os'})

    def test_every_deviation_has_a_removal_condition(self):
        text=(ROOT/'docs/deviations.md').read_text()
        ids=re.findall(r'^\| (DEV-\d+) \|',text,re.M)
        self.assertEqual(len(ids),13)
        self.assertEqual(len(ids),len(set(ids)))
        self.assertIn('Removal or replacement condition',text)

if __name__=='__main__':unittest.main()
