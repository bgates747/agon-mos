// MOS-owned diagnostic addition to Agon VDP 2.16.0. SPDX-License-Identifier: MIT
#pragma once
#pragma push_macro("UART_RX_SIZE")
#undef UART_RX_SIZE
#include <driver/uart.h>
#pragma pop_macro("UART_RX_SIZE")
#include <esp_timer.h>
#include <hal/uart_ll.h>
#include <soc/uart_struct.h>
extern "C" {
void uart0_race_arm(unsigned);
unsigned uart0_race_state(void);
void uart0_race_snapshot(uint8_t *);
void uart0_race_escape(void);
void uart0_race_collect(uint8_t *);
}
namespace Uart0Race {
static uint8_t report[160];
static void put32(unsigned at,uint32_t n){for(unsigned i=0;i<4;i++)report[at+i]=n>>(i*8);}
static uint32_t crc_byte(uint32_t c,uint8_t b){c^=b;for(unsigned i=0;i<8;i++)c=(c>>1)^((c&1)?0xedb88320U:0);return c;}
}
void VDUStreamProcessor::uart0Race() {
    using namespace Uart0Race;
    auto action=readByte_t();
    if(action==2){uint8_t p[]={0xd6};send_packet(PACKET_GP,1,p);return;}
    if(action==1){
        auto index=readByte_t(),half=readByte_t();
        if(index<0||index>=160||half<0||half>1)return;
        uint8_t p[]={uint8_t((report[index]>>(half*4))&15)};send_packet(PACKET_GP,1,p);return;
    }
    if(action!=0)return;
    auto mode=readByte_t(),reserved=readByte_t();
    if(mode<0||mode>1||reserved!=0)return;
    memset(report,0,sizeof(report));memcpy(report,"URD1",4);report[4]=1;report[5]=mode;
    size_t buffered=0;uart_get_buffered_data_len(UART_NUM_2,&buffered);
    if(buffered||uart_ll_get_rxfifo_len(&UART2)){uint8_t p[]={0xe2};send_packet(PACKET_GP,1,p);return;}
    uart0_race_arm(mode);uint8_t armed[]={0xe1};send_packet(PACKET_GP,1,armed);
    // Let the actual ISR fill the unchanged 256-byte software ring. Core0
    // reader then uses the normal IDF recovery path while core1 ISR runs.
    int64_t start=esp_timer_get_time();
    while(!(uart0_race_state()&1) && esp_timer_get_time()-start<50000) {}
    uint32_t received=0,crc=0xffffffffU;bool ended=false,extra=false,captured=false,escaped=false;
    uint8_t bytes[128];int64_t deadline=esp_timer_get_time()+3000000,last=esp_timer_get_time();
    while(esp_timer_get_time()<deadline){
        int count=uart_read_bytes(UART_NUM_2,bytes,sizeof(bytes),0);
        if(count>0){
            last=esp_timer_get_time();
            for(int i=0;i<count;i++){
                if(bytes[i]==0)ended=true;
                else if(ended)extra=true;
                else {++received;crc=crc_byte(crc,bytes[i]);}
            }
        } else {
            if(!captured && esp_timer_get_time()-last>20000){
                uart0_race_snapshot(report);captured=true;
                // Snapshot before rescue; empty ring/false flag plus pending,
                // masked RX and unread FIFO is the independently checked oracle.
                auto hw=&UART2;
                if(uart_ll_get_rxfifo_len(hw) && !(hw->int_ena.val&0x101) && (hw->int_raw.val&0x101)){
                    uart0_race_escape();escaped=true;last=esp_timer_get_time();
                }
            }
            if(ended && esp_timer_get_time()-last>20000)break;
            delay(1);
        }
    }
    if(!captured)uart0_race_snapshot(report);
    uart0_race_collect(report);
    put32(8,received);put32(12,crc^0xffffffffU);
    report[60]=escaped;report[62]=(ended?1:0)|(extra?2:0);
    // Result code: control completed, triggered state captured, inconclusive,
    // or payload transport failed. Detailed validity is checked by the host.
    report[7]=ended&&!extra?(mode?(escaped?2:3):(escaped?3:1)):4;
    uint8_t done[]={0xe3};send_packet(PACKET_GP,1,done);
}
