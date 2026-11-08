"""Bounded host controls for the independent wire oracle and script syntax."""
from pathlib import Path
import ast,importlib.util,json
here=Path(__file__).resolve().parent
for source in here.glob('*.py'):ast.parse(source.read_text(),filename=str(source))
spec=importlib.util.spec_from_file_location('wire',here/'check_wire.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
key_down=bytes([0x81,4,ord('a'),0,1,1]);key_up=bytes([0x81,4,ord('a'),0,1,0])
frames=b''.join(bytes([0x90])+n.to_bytes(2,'little')+bytes((i*157+7)&255 for i in range(n))for n in m.SIZES)
# Real startup already emits an unrelated key release before the app. Parse
# it normally, but count synthetic keyboard events only between ordered fences.
prefix=bytes([0x81,4,0,0,117,0,0x80,1,0x30]);suffix=bytes([0x80,1,0x34])
stream=prefix+frames+key_down+key_up+suffix
report='\n'.join('Case counted '+str(i)for i in range(10))+'\nRX005 RESULT callbacks=30 work=42 keys=1/1 regfail=0 ifffail=0\nRX005 KEY PASS down=1 up=1 bulk=512\nRX005 SUITE PASS\n'
positive=m.verify(stream,report)
corrupt=bytearray(stream);corrupt[len(prefix)+6]^=1
negative=[('payload corruption',bytes(corrupt),report),('truncated body',stream[:-1],report),('unframed prefix',b'\x01'+stream,report),('duplicate frame',prefix+b'\x90\x00\x00'+frames+key_down+key_up+suffix,report),('missing genuine key',prefix+frames+key_down+suffix,report),('wrong callback total',stream,report.replace('callbacks=30','callbacks=29')),('register failure',stream,report.replace('regfail=0','regfail=1')),('missing end fence',stream[:-len(suffix)],report)]
rejected=[]
for label,data,text in negative:
 try:m.verify(data,text)
 except AssertionError:rejected.append(label)
 else:raise AssertionError('Oracle accepted '+label)
print(json.dumps({'schema':'RX005-host-oracle-controls-1','positive':positive,'negative_rejected':rejected,'target_execution':False},indent=2))
