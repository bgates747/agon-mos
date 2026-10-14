"""Strict versioned recovery report reader; no physical race-exclusion claim."""
import json,sys
from pathlib import Path

def analyze(data:bytes):
    assert len(data)==608 and data[:9]==b'URXHOST1\x01','Invalid report size/version'
    u24=lambda b,o:int.from_bytes(b[o:o+3],'little')
    state=dict(stage=data[9],total_cases=data[10],completed=data[11],active_case=data[12],repeats=data[13],failure_code=data[14],baseline_rx=data[15],checkpoint_tick=u24(data,16),last_progress_tick=u24(data,19),last_accepted=u24(data,22),packets_completed=u24(data,25),wire_bytes=u24(data,28))
    assert state['repeats'] in (1,4) and state['total_cases']==6*state['repeats']
    assert state['completed']<=state['total_cases'] and state['stage'] in range(5)
    rows=[]
    for i in range(state['completed']):
        r=data[32+i*24:56+i*24];mode=i%2;kind=i%6//2;wire=[525184,8576,8448][kind]
        assert r[:3]==bytes([mode,kind,i]) and r[3]==r[7]==0 and r[23]==1
        assert r[4]==r[5]==(32 if kind==1 else 0) and r[6]<=r[5]
        assert kind!=1 or not mode or r[6]>0,'No concurrent reply observed in async duplex'
        assert u24(r,8)>0 and u24(r,11)==u24(r,14)==wire and u24(r,17)==(32 if kind else 64) and u24(r,20)==8192
        rows.append(dict(case=i+1,mode=mode,kind=kind,ticks=u24(r,8),wire_bytes=wire,verified_final_buffer_bytes=8192,replies=r[5],replies_while_busy=r[6],rx_errors=r[3]))
    passed=state['stage']==0 and state['completed']==state['total_cases'] and not state['failure_code']
    return dict(state=state,campaign_passed=passed,records=rows,final_buffer_bytes_checked=8192*len(rows),intermediate_bulk_payloads_verified=False,physical_race_ruled_out=False,receiver_race_attributed=False)
if __name__=='__main__':print(json.dumps(analyze(Path(sys.argv[1]).read_bytes()),indent=2))
