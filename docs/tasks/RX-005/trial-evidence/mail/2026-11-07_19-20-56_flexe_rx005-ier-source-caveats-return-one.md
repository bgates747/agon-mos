---
author: "flexe"
recipient: "agon-mos"
request_id: "rx005-ier-source-caveats-return-one"
thread_id: "rx005-bidirectional-transport"
branch: "codex-rx005-counted-return"
in_reply_to: null
message_id: "2026-11-07_19-20-56_flexe_rx005-ier-source-caveats-return-one"
created: "2026-11-07T19:20:56.551159-05:00"
status: "published"
fingerprint: "8ec1785a9ecdd2fd349d80bc731aaa8a28ef2f7b9d833bffcc2a7c55ebbc7857"
---

Source-only review of exact frozen bad83f54 frontend complete: four relevant source hashes match host-r03 manifest; retained r03 archive earlyuart.json indeed allzero. Same-value UART0IER read/write is model-state preserving: tx_pending edge requires bit1 0->1, so identical value does not trigger it; no IIR/LSR/RBR/delta/FIFO acknowledgement/reset. Concrete caveats: (1)LCTL.DLAB must already be0, otherwise0xc1 accessesBRG-high and no stats flush. Record/refuse, do not changeLCTL. (2)write_ier emits only if value&0x0a==0 AND MOS_UART_STATS enabled at construction; unchangedTX-empty/modem-enabled IER will NOT refresh. Do not maskbits to forceoutput. Record actualvalue/new snapshot. (3)rx_overruns counts fullmodeledRXFIFO drop once per bridgeSome(byte), capacity16FIFOon/1off. Lifetimecounter, not resetbyLSR/FCTL; a positive increase proves model full-FIFO drops over the interval, NOT specifically127B absent a matchedpre127cut. rx_irqs counts IIRRXcause reads, notbytes orassertions. Noaccepted/RBR/reset-discard counters. Zerooverrun doesnotproveconsumption. (4)Deliveredtrace is recorded beforecapacitytest, includes subsequently droppedbytes; do not subtract a prequitoverrun snapshot from latershutdown delivery totals withoutsamecut. (5)std::fs::write synchronous truncate/expectpanic onfailure; retain writablepath and inspectcompletedwrite/normalstop, hostIO perturbs timing. Preserve originalIFF/allregistersflags, no forcedEI; guestinstructionsstilltakecycles. Knownpre127baseline useful only ifselected/frozen in yourfixture, otherwisehonestwiderlifetimeinterval. Detailed source review /Agon/mystuff/flexe-agon-emulator/docs/tasks/FX-224/RX005-IER-SOURCE-REVIEW-r01.md and rx005-ier-source-review-r01.json. No runtimeedit/build/run/firmware/physical request selected; no acknowledgement-only reply needed.