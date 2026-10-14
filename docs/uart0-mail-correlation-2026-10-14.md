# Recent UART/race mail correlation

Executive summary: multiple projects report communication stalls, but they do
not all have the same demonstrated cause. UART/Flexe has a traced receive race
in the emulator. Rally has a similar startup stall and the same vulnerable
firmware ordering, with attribution still unproven for its closed run. Fsim's
P4/ExCom failure is an independently identified packet-format error. None of
these reports establishes the suspected receive race on physical Console8.

Read all 11 matching immutable messages between approximately02:01 and04:01
America/New_York on2026-10-14, including incidental UART/recovery references.
The read-only inventory/body snapshot is retained at
`build/uart0-recovery/recent-uart-mail.json`. No other recipient's mail was
acknowledged and no peer source or hardware was changed.

| Project/report | Evidence | Attribution |
|---|---|---|
| MOS UART0 / Flexe FX-006 | Independent store-order histories show reader recovery before delayed ISR RX disable; diagnostic re-enable releases backpressure | Demonstrated in captured emulator executions; no physical-board trace |
| Rally full-scene startup | Identical passing/failed ingress prefix; sign-art WRITE declares2048bytes but only416arrive. No native game module started. Exact firmware disassembly has the same flag-before-lock ordering | Strong shared-race lead; no live FIFO/mask/ring state or write history for the closed human run |
| Fsim P4 / ExCom P058 | KEY packet length10 conflicts with EMOS's required length4; exact packet rejects in receiver harness. GP-based replacement prepared | Different application/bridge protocol defect; not evidence of the UART recovery race |
| Rally earlier physical fixture |900requests/3600physics ticks and complete returned state pass on Console8 | Passing workload only; not a receiver-race exclusion or full-scene hardware result |

Decisive recent correspondence:

- [Rally startup failure](../../agon-dev-env/cross-agent/agentcoms/messages/2026-10-14_03-32-16_rally_rally25-full-scene-human-startup-stall-fifty-two.md).
- [Golem exact-ELF correlation](../../agon-dev-env/cross-agent/agentcoms/messages/2026-10-14_03-53-42_golem_rally25-startup-uart-correlation-thirty.md).
- [Fsim malformed completion carrier](../../agon-dev-env/cross-agent/agentcoms/messages/2026-10-14_03-23-46_fsim_fsim-pingo-p4-carrier-root-cause-ten.md).
- [Fsim GP replacement prepared](../../agon-dev-env/cross-agent/agentcoms/messages/2026-10-14_03-55-38_fsim_fsim-pingo-p4-gp-repair-eleven.md).
- [Earlier Rally physical pass](../../agon-dev-env/cross-agent/agentcoms/messages/2026-10-14_02-19-32_rally_rally25-console8-hardware-qualified-forty-five.md).

Rally's failed receiver is a different exact ELF from MOS's traced image.
Golem independently derived the matching instruction addresses; address equality
is not evidence that complete firmware images are identical. Rally's sender
uses stock MOS, so this symptom is not confined to our experimental async driver.
That observation strengthens the shared receiver investigation, not attribution
of Rally's particular stall or a claim of a physical VDP defect.

HW-001 preparation continues with valid stock commands, unchanged stock VDP,
explicit final-buffer integrity coverage and progress checkpoints. A stall
must be recorded as a communication failure pending receiver-state evidence.
A passing test cannot rule out a rare race. The plan and sole TODO retain these
interpretation boundaries; no new competing task checklist is created here.
