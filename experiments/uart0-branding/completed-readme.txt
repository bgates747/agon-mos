CONSOLE8 UART CAMPAIGN COMPLETE

C8-002 [x] Three A/B runs PASS: R0026, R0027, R0028 (90 phases).
C8-003 [x] Compatibility PASS: R0029, including final-buffer checks.
Tested MOS: unbranded API1.1, ROM CRC239097B7.
Full history is archived in the project. No repeat needed for branding alone.

C8-005 [ ] Optional: install the branded experimental MOS when convenient.
CD /test/mos-uart0
LOAD test.bin
RUN
Choose 9 -> 1 for mos-candidate.bin, then reboot.
Require MOS subtitle: Arthur - UART0 async EXPERIMENTAL
Reload menu: expect ROM CRC44BC5C07, API1.1.
The flash utility shows FILE CRC AD9C0F96 (different from full ROM CRC).

C8-004 [x] Stock restore superseded: Author installed another project's VDP.
Leave that VDP alone for branding. No VDP flash or UART rerun requested here.
Root /MOS.bin is stock; do not use it for the experimental UART sender.
