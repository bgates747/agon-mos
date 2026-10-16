"""Decode captured driver evidence; diagnostic-induced ordering is explicit."""
import json,sys,zlib
from pathlib import Path
u32=lambda b,o:int.from_bytes(b[o:o+4],'little')
expected_crc=zlib.crc32(bytes(((n*157+7)%254)+1 for n in range(4096)))
def analyze(data):
    assert len(data)==332 and data[:9]==b'URDHOST1\x01' and data[10]==2
    result=dict(stage=data[9],completed=data[11],cases=[],physical_race_ruled_out=False,natural_stock_failure_reproduced=False)
    for i in range(data[11]):
        r=data[12+i*160:172+i*160];assert r[:6]==b'URD1'+bytes([1,i])
        events=[dict(type=e[0],core=e[1],full_flag=e[2],fifo=e[3],enabled=u32(e,4),raw=u32(e,8),buffered=u32(e,12),stash=u32(e,16),cycles=u32(e,20)) for e in [r[64+j*24:88+j*24] for j in range(4)]]
        pub,reader,masked,escape=events
        integrity=(u32(r,8)==4096 and u32(r,12)==expected_crc and not u32(r,16) and not r[61] and r[62]==1)
        cores=(pub['core'] in (0,1) and pub['core']==masked['core'] and reader['core']==1-pub['core'] and r[52]==pub['core'] and r[53]==reader['core'])
        common=(pub['type']==1 and reader['type']==2 and masked['type']==3 and pub['full_flag']==1 and reader['full_flag']==0 and reader['enabled']&0x101==0x101 and r[54]==1 and r[55]==64 and u32(r,56)&0x101==0x101)
        control=(r[7]==1 and r[6]==3 and not r[60] and masked['full_flag']==1 and masked['enabled']&0x101==0 and escape['type']==0)
        forced=(r[7]==2 and r[6]==4 and r[60]==1 and u32(r,20)==7 and masked['full_flag']==0 and masked['enabled']&0x101==0 and 0<u32(r,24)<=128 and u32(r,28)&0x101==0 and u32(r,32)&0x101!=0 and u32(r,36)==0 and u32(r,40)==0 and u32(r,48)==0 and escape['type']==4 and escape['enabled']&0x101==0x101)
        result['cases'].append(dict(mode=i,outcome=r[7],received=u32(r,8),crc32=f'{u32(r,12):08X}',RX_errors=u32(r,16),MOS_RX_errors=r[61],driver_state=u32(r,20),integrity_passed=integrity,actual_other_core_recovery=cores,evidence_valid=bool(integrity and cores and common and (forced if i else control)),pre_escape=dict(fifo=u32(r,24),enabled=u32(r,28),raw=u32(r,32),full_flag=u32(r,36),buffered=u32(r,40),stash=u32(r,44),remaining=u32(r,48)),events=events))
    result['protocol_complete']=data[9]==0 and data[11]==2
    result['diagnostic_evidence_valid']=result['protocol_complete'] and all(r['evidence_valid'] for r in result['cases'])
    return result
if __name__=='__main__':print(json.dumps(analyze(Path(sys.argv[1]).read_bytes()),indent=2))
