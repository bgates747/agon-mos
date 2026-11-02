"""Short SDL taps through compiled VDP/MOS keymap, plus actual display capture."""
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2]
p=root/'experiments/uart0-balls/qualify_flexe.py';s=p.read_text()
# Compose the existing finite runner, then adapt its lifecycle to interaction.
s=s.replace("exec(compile(s,str(__file__),'exec'))",'''s=s.replace("('uart0-balls-'+a.engine+'-'+a.attempt)","('uart0-balls-ui-'+a.engine+'-'+a.attempt)")
s=s.replace("('sweep' if a.sweep else 'quick')", "''")
needle="started=time.monotonic();proc=None;error=None;art=profile/'last-run'"
s=s.replace(needle,needle+";keys=out/'keys';keys.write_bytes(b'');capture=out/'capture'")
s=s.replace("AGON_FLEXE_ENGINE=a.engine)","AGON_FLEXE_ENGINE=a.engine,LD_PRELOAD=str(root/'build/uart0-balls/input.so'),UART_SUITE_KEYS=str(keys),BALLS_CAPTURE=str(capture))")
needle="  last=time.monotonic();previous=0"
s=s.replace(needle,"""  cursor=0
  def wait_for(marker,timeout=15):
   global cursor
   end=time.monotonic()+timeout
   while time.monotonic()<end:
    path=art/'mos-to-vdp.bin';data=path.read_bytes() if path.exists() else b''
    at=data.find(marker,cursor)
    if at>=0:cursor=at+len(marker);return
    assert proc.poll() is None,'Emulator exited'
    time.sleep(.02)
   raise TimeoutError(repr(marker))
  def tap(key,marker):
   with keys.open('ab') as handle:handle.write(b'#'+key)
   wait_for(marker)
  wait_for(b'Balls 24  - / =')
  time.sleep(.25)
  tap(b'2',b'2 ASYNC EVENTS')
  tap(b'3',b'3 ASYNC CALLBACK')
  tap(b'b',b'VDP CIRCLES')
  tap(b'c',b'C: BALL COLLISIONS')
  tap(b'=',b'Balls 28  - / =')
  tap(b'-',b'Balls 24  - / =')
  time.sleep(1)
  capture.touch()
  until=time.monotonic()+5
  while capture.exists() and time.monotonic()<until:time.sleep(.02)
  assert (out/'capture.ppm').exists(),'No display captured'
  tap(b'r',b'3 ASYNC CALLBACK')
  tap(b'1',b'1 STANDARD')
  tap(b'q',b'BALLS DEMO COMPLETE')
"""+needle)
a=s.index("  command=[sys.executable");z=s.index("\\n stats=json.loads",a)
s=s[:a]+"  report=(reports/'R0001.log').read_text();assert 'END PASS' in report and 'key_overruns=0' in report\\n"+s[z:]
s=s.replace("ordered_replies=192 if a.sweep else 48","ordered_replies=None")
exec(compile(s,str(__file__),'exec'))''')
exec(compile(s,str(p),'exec'))
