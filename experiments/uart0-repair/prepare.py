"""Export three private VDP builds; upstream and installed SDK stay read-only."""
import difflib,hashlib,json,shutil
from pathlib import Path
from patch_driver import repair,ORIGINAL_SHA256

root=Path(__file__).resolve().parents[2];b=root/'build/uart0-repair'
source=root/'build/uart0-race/firmware'
original=(root/'build/uart0-race/uart-idf-4.4.6.c').read_text()
assert hashlib.sha256(original.encode()).hexdigest()==ORIGINAL_SHA256
prior=json.loads((root/'build/uart0-race/source.json').read_text())
for name,pin in prior['files'].items():assert hashlib.sha256((source/name).read_bytes()).hexdigest()==pin,name
b.mkdir(parents=True,exist_ok=True)
(b/'original-uart.c').write_text(original)
fixed=repair(original);(b/'fixed-uart.c').write_text(fixed)
(b/'uart-rx-full-lock.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),fixed.splitlines(True),fromfile='a/uart.c',tofile='b/uart.c')))
def replace(text,old,new):
    assert text.count(old)==1,old
    return text.replace(old,new)
for variant in ('before','fixed','candidate'):
    fw=b/variant;assert not fw.exists()
    shutil.copytree(source,fw,ignore=shutil.ignore_patterns('.pio','.git'))
    (fw/'video/uart0_diag_driver.c').unlink()
    driver=original if variant=='before' else fixed
    ini=(fw/'platformio.ini').read_text().replace('build_flags =','build_flags =\n    -DUART0_RX_REPAIRED='+str(int(variant!='before')))
    (fw/'platformio.ini').write_text(ini)
    if variant=='candidate':
        for n in ('uart0_race.h','uart0_race_hooks.h'):(fw/'video'/n).unlink()
        path=fw/'video/vdu_sys.h';s=path.read_text();s=replace(s,'#include "uart0_race.h"','')
        identity='case 0xE6: { auto action=readByte_t(); if(action==2){ uint8_t p[]={0xda}; send_packet(PACKET_GP,1,p); } } break;'
        s=replace(s,'case 0xE6: { uart0Race(); } break;',identity);path.write_text(s)
        path=fw/'video/vdu_stream_processor.h';path.write_text(replace(path.read_text(),'        void uart0Race();',''))
    else:
        for n,src in [('uart0_race.h','receiver.h'),('uart0_race_hooks.h','driver-hooks.h')]:shutil.copyfile(root/'experiments/uart0-repair'/src,fw/'video'/n)
        driver=replace(driver,'static portMUX_TYPE uart_selectlock = portMUX_INITIALIZER_UNLOCKED;','#include "uart0_race_hooks.h"\nstatic portMUX_TYPE uart_selectlock = portMUX_INITIALIZER_UNLOCKED;')
        publication='p_uart->rx_buffer_full_flg = true;\n                    race_after_publish(uart_num);'
        if variant=='before':publication+='\n                    race_wait_after_update(uart_num);'
        driver=replace(driver,'p_uart->rx_buffer_full_flg = true;',publication)
        mask='uart_hal_disable_intr_mask(&(uart_context[uart_num].hal), UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);'
        driver=replace(driver,mask,mask+'\n                    race_after_mask(uart_num);')
        if variant=='fixed':
            end='race_after_mask(uart_num);\n                    UART_EXIT_CRITICAL_ISR(&(uart_context[uart_num].spinlock));'
            driver=replace(driver,end,end+'\n                    race_wait_after_update(uart_num);')
        recovery='uart_reenable_intr_mask(p_uart_obj[uart_num]->uart_num, UART_INTR_RXFIFO_TOUT | UART_INTR_RXFIFO_FULL);'
        driver=replace(driver,recovery,recovery+'\n            race_after_recovery(uart_num);')
        status='uart_intr_status = uart_hal_get_intsts_mask(&(uart_context[uart_num].hal));'
        driver=replace(driver,status,status+'\n        race_note_interrupt(uart_num,uart_intr_status);')
    (fw/'video/uart0_rx_driver.c').write_text(driver)
    path=fw/'video/version.h';banner={'before':'UART0 baseline diagnostic','fixed':'UART0 repaired diagnostic','candidate':'UART0 RX sync candidate'}[variant]
    path.write_text(replace(path.read_text(),'UART0 recovery diagnostic',banner))
    pins={str(p.relative_to(fw)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(fw.rglob('*')) if p.is_file()}
    (b/f'{variant}-source.json').write_text(json.dumps(dict(variant=variant,VDP_commit=prior['vdp_commit'],vdp_gl_commit=prior['vdp_gl_commit'],IDF=prior['idf'],original_driver_sha256=ORIGINAL_SHA256,fixed_driver_sha256=hashlib.sha256(fixed.encode()).hexdigest(),files=pins),indent=2)+'\n')
    print('Prepared',variant,flush=True)
