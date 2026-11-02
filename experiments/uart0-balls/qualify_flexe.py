"""Finite headless balls sweep, using the established pinned runtime lifecycle."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'experiments/uart0-startup-safe'))
p=root/'experiments/uart0-startup-safe/flexe.py';s=p.read_text()
s=s.replace("p.add_argument('--wrong-rom',action='store_true')", "p.add_argument('--wrong-rom',action='store_true');p.add_argument('--sweep',action='store_true');p.add_argument('--maintained',action='store_true')")
s=s.replace("default='fixture2'","default='fixture'")
s=s.replace("old=root/'.emulator/uart0-race'", "old=(root/'build/uart0-balls/runtime-maintained') if a.maintained else (root/'.emulator/uart0-race')")
s=s.replace("=='412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9'", "==('7e7d0e1bc89af72bde7ffbd6c06446aaefda4d1803f89eb1faf3167307ee1e01' if a.maintained else '412089a89a5adccb3c1c0fc4b121472da28f2d3d48c435c88a660028d7cd84d9')")
s=s.replace("=='77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd'", "==('0866265bd6f3d73ad572f31dc1bb954f308ed9a5d857efa9414d37e1ade13374' if a.maintained else '77b3cbf76564d54628c2bb876aa96ef3834c6b363d53df4892b8a3ab4248e5cd')")
s=s.replace("result=dict(passed=", "result=dict(frontend_sha256=h(files['flexe-agon-emulator.bin']),backend_sha256=h(files['flexe-vdp.so']),passed=")
s=s.replace("('uart0-startup-safe-'+a.engine+'-'+a.attempt)","('uart0-balls-'+a.engine+'-'+a.attempt)")
s=s.replace("for name in ('test.bin','stress.bin','app.bin','checks.bin'):put(f/name,'uart0/'+name)","put(f/'bin/balls.bin','uart0/test.bin')")
start=s.index("startup=out/'autoexec.txt';");end=s.index(";(profile/'sdcard.img').symlink_to(card)",start)
s=s[:start]+'''startup=out/'autoexec.txt';startup.write_bytes(('CD /uart0\\r\\nLOAD test.bin\\r\\nRUN . '+('sweep' if a.sweep else 'quick')+'\\r\\nDIR\\r\\nECHO BALLS AUTOMATION RETURN\\r\\n').encode());put(startup,'autoexec.txt')'''+s[end:]
s=s.replace("b'UART0 STARTUP-SAFE SUITE FAIL'","b'BALLS DEMO FAIL'")
s=s.replace("b'STARTUP SAFE CAMPAIGN RETURN'","b'BALLS AUTOMATION RETURN'")
start=s.index('  assert wire.count(');end=s.index('\n stats=json.loads',start)
s=s[:start]+'''  assert wire.count(b'BALLS DEMO COMPLETE - numbered report saved')==1
  assert b'BALLS AUTOMATION RETURN' in wire
  assert (reports/'R0001.log').exists()
  assert int((reports/'next.txt').read_text())==2
  journal=(reports/'runs.log').read_text();assert 'START run=0001' in journal and 'END run=0001 PASS' in journal
  command=[sys.executable,str(root/'experiments/uart0-balls/analyze.py'),str(reports/'R0001.log'),'--output',str(out/'analysis.json')]
  if not a.sweep:command.append('--quick')
  subprocess.run(command,check=True)
'''+s[end:]
s=s.replace("h(f/'test.bin')","h(f/'bin/balls.bin')")
s=s.replace('receiver_bytes_compared=65536 if verified else 0,ordered_replies=256 if verified else 0','receiver_bytes_compared=None,ordered_replies=192 if a.sweep else 48')
exec(compile(s,str(__file__),'exec'))
