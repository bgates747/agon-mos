"""Reuse the frozen-runtime runner with callback-fixture and counter oracles."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'experiments/uart0-startup-safe'))
p=root/'experiments/uart0-startup-safe/flexe.py';s=p.read_text()
s=s.replace("p.add_argument('--wrong-rom',action='store_true')", "p.add_argument('--wrong-rom',action='store_true');p.add_argument('--first-report',type=int,default=1);p.add_argument('--repeat',type=int,default=1)")
s=s.replace("assert a.attempt.isalnum()", "assert a.attempt.isalnum() and 1<=a.first_report<10000 and 1<=a.repeat<=2 and a.first_report+a.repeat<=10000")
s=s.replace("('uart0-startup-safe-'+a.engine+'-'+a.attempt)","('uart0-completion-'+a.engine+'-'+a.attempt)")
old="b'CD /uart0\\r\\nLOAD test.bin\\r\\nRUN . 0\\r\\nECHO FIRST STOCK CLI RETURN\\r\\nLOAD test.bin\\r\\nRUN . 0\\r\\nDIR\\r\\nECHO STARTUP SAFE CAMPAIGN RETURN\\r\\n'"
new="('CD /uart0\\r\\n'+('LOAD test.bin\\r\\nRUN .\\r\\n'*a.repeat)+'DIR\\r\\nECHO STARTUP SAFE CAMPAIGN RETURN\\r\\n').encode('ascii')"
assert old in s;s=s.replace(old,new)
# Seed only the explicitly requested cleaned-card numbering control.
needle="(profile/'sdcard.img').symlink_to(card)"
s=s.replace(needle,"counter=out/'next.txt';counter.write_text(str(a.first_report)+'\\n');put(counter,'uart0/next.txt');"+needle)
s=s.replace("b'UART0 STARTUP-SAFE SUITE FAIL'", "b'END CALLBACK SUITE FAIL'")
a=s.index('  assert wire.count(');z=s.index('\n stats=json.loads',a)
s=s[:a]+'''  assert wire.count(b'END CALLBACK SUITE PASS')==a.repeat
  assert b'STARTUP SAFE CAMPAIGN RETURN' in wire
  for n in range(a.first_report,a.first_report+a.repeat):
   report=(reports/f'R{n:04}.log').read_text()
   assert 'Comparator negative/positive controls PASS.' in report
   assert report.count('Case PASS: full receiver bytes and notification count.')==4
   assert 'END CALLBACK SUITE PASS' in report
  assert len(list(reports.glob('R*.log')))==a.repeat
  assert int((reports/'next.txt').read_text())==a.first_report+a.repeat
  journal=(reports/'runs.log').read_text();assert journal.count('END CALLBACK SUITE PASS')==a.repeat
'''+s[z:]
s=s.replace('receiver_bytes_compared=65536 if verified else 0,ordered_replies=256 if verified else 0','receiver_bytes_compared=32768*a.repeat if verified else 0,ordered_replies=None')
exec(compile(s,str(__file__),'exec'))
