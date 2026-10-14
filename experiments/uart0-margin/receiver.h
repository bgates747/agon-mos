// MOS-owned diagnostic addition to Agon VDP 2.16.0. SPDX-License-Identifier: MIT
// UART2 RX interrupt servicing is suspended for a bounded interval only.
// Hardware RTS remains enabled. No FIFO reset or global interrupt masking.
#pragma once
#pragma push_macro("UART_RX_SIZE")
#undef UART_RX_SIZE
#include <driver/uart.h>
#pragma pop_macro("UART_RX_SIZE")
#include <esp_timer.h>
#include <hal/uart_ll.h>
#include <soc/uart_struct.h>
#include <soc/uart_reg.h>

namespace Uart0Margin {
static uint8_t report[48];
static constexpr uint32_t errors=UART_RXFIFO_OVF_INT_RAW_M|UART_FRM_ERR_INT_RAW_M|UART_PARITY_ERR_INT_RAW_M|UART_BRK_DET_INT_RAW_M;
static constexpr uint32_t rx_mask=errors|UART_RXFIFO_FULL_INT_ENA_M|UART_RXFIFO_TOUT_INT_ENA_M;
static void put32(unsigned at,uint32_t n){for(unsigned i=0;i<4;i++)report[at+i]=n>>(i*8);}
static uint32_t crc_byte(uint32_t c,uint8_t b){c^=b;for(unsigned i=0;i<8;i++)c=(c>>1)^((c&1)?0xedb88320U:0);return c;}
}

void VDUStreamProcessor::uart0Margin() {
    using namespace Uart0Margin;
    auto action=readByte_t();
    if(action==2){uint8_t p[]={0xe7};send_packet(PACKET_GP,1,p);return;}
    if(action==1){
        auto index=readByte_t(),half=readByte_t();
        if(index<0||index>=48||half<0||half>1)return;
        uint8_t p[]={uint8_t((report[index]>>(half*4))&15)};
        send_packet(PACKET_GP,1,p);return;
    }
    if(action!=0)return;
    auto threshold=readByte_t(),hold_ms=readByte_t();
    if(threshold<1||threshold>127||hold_ms<1||hold_ms>20)return;
    memset(report,0,sizeof(report));memcpy(report,"URM1",4);
    report[4]=1;report[5]=threshold;report[6]=hold_ms;
    uart_dev_t* hw=UART_LL_GET_HW(UART_NUM_2);
    const uint32_t saved_enable=hw->int_ena.val;
    const uint32_t saved_conf1=hw->conf1.val;
    // Payload is not published until the ARMED reply. No buffered payload is
    // allowed before masking, otherwise FIFO occupancy would be misleading.
    size_t buffered=0;uart_get_buffered_data_len(UART_NUM_2,&buffered);
    report[7]=uint8_t(uart_ll_get_rxfifo_len(hw));
    put32(8,buffered);put32(12,hw->int_raw.val&errors);
    if(buffered||report[7]){report[44]=1;uint8_t p[]={0xe2};send_packet(PACKET_GP,1,p);return;}
    if(uart_disable_intr_mask(UART_NUM_2,rx_mask)!=ESP_OK){report[44]=2;uint8_t p[]={0xe2};send_packet(PACKET_GP,1,p);return;}
    // Change only the receiver threshold. Preserve CTS/RTS enable and all
    // other UART configuration, and record the exact hardware readback.
    hw->conf1.rx_flow_thrhd=threshold;
    report[16]=hw->conf1.rx_flow_thrhd;
    report[17]=hw->conf1.rx_flow_en;
    put32(18,hw->int_ena.val&rx_mask);
    const int64_t start=esp_timer_get_time();
    uint8_t armed[]={0xe1};send_packet(PACKET_GP,1,armed);
    uint32_t last_count=uart_ll_get_rxfifo_len(hw),peak=last_count;
    int64_t changed=start;
    while(esp_timer_get_time()-start<int64_t(hold_ms)*1000){
        uint32_t count=uart_ll_get_rxfifo_len(hw);
        if(count!=last_count){changed=esp_timer_get_time();last_count=count;}
        if(count>peak)peak=count;
    }
    const int64_t stopped=esp_timer_get_time();
    report[22]=uint8_t(peak);report[23]=uint8_t(uart_ll_get_rxfifo_len(hw));
    put32(24,hw->int_raw.val&errors);
    put32(28,uint32_t(stopped-start));put32(32,uint32_t(stopped-changed));
    // Restore BEFORE verification, even when overflow has occurred. Raw
    // payload is drained here rather than passed into the VDU parser.
    hw->conf1.rx_flow_thrhd=(saved_conf1>>UART_RX_FLOW_THRHD_S)&UART_RX_FLOW_THRHD_V;
    const esp_err_t restored=uart_enable_intr_mask(UART_NUM_2,saved_enable&rx_mask);
    // The resumed IDF ISR may legitimately change its enable mask immediately.
    // Check our threshold/flow settings and the API result, not that racing mask.
    report[45]=(restored==ESP_OK &&
        hw->conf1.rx_flow_thrhd==((saved_conf1>>UART_RX_FLOW_THRHD_S)&UART_RX_FLOW_THRHD_V) &&
        hw->conf1.rx_flow_en==((saved_conf1>>UART_RX_FLOW_EN_S)&UART_RX_FLOW_EN_V));
    uint32_t received=0,crc=0xffffffffU;bool ended=false,extra=false;
    uint8_t bytes[128];
    int64_t last=esp_timer_get_time(),deadline=last+3000000;
    while(esp_timer_get_time()<deadline){
        // Metadata was consumed through HardwareSerial without peeking, and
        // no payload was buffered at arm time. Use the underlying IDF driver
        // directly here: bounded nonblocking chunk reads avoid a per-byte
        // Arduino mutex and still use the installed receiver/ring buffer.
        int count=uart_read_bytes(UART_NUM_2,bytes,sizeof(bytes),0);
        if(count>0){
            last=esp_timer_get_time();
            for(int i=0;i<count;i++){
                if(bytes[i]==0)ended=true;
                else if(ended)extra=true;
                else {++received;crc=crc_byte(crc,bytes[i]);}
            }
        } else {
            if(ended && esp_timer_get_time()-last>20000)break;
            delay(1);
        }
    }
    put32(36,received);put32(40,crc^0xffffffffU);
    if(!ended)report[44]|=4;
    if(extra)report[44]|=8;
    if(!report[45])report[44]|=16;
    // Measurement validity is separate from byte-integrity success. Emulator
    // protocols can work even when the hardware FIFO/RTS model is inadequate.
    report[46]=(report[16]==threshold && report[17] &&
        !report[18]&&!report[19]&&!report[20]&&!report[21] &&
        report[7]==0 && !buffered && !report[12]&&!report[13]&&!report[14]&&!report[15] && peak<=128 && peak>uint32_t(threshold) &&
        report[32]+(uint32_t(report[33])<<8)+(uint32_t(report[34])<<16)+(uint32_t(report[35])<<24)>=200);
    uint8_t done[]={0xe3};send_packet(PACKET_GP,1,done);
}
