# Pertinent Discord discussion: simple bidirectional UART transport

Imported2026-11-07. Full unchanged source: [discord-transcript.txt](discord-transcript.txt).
Original attachment:
`/Agon/mystuff/agent-state/codex/attachments/97f30617-c405-4d28-b387-252301aeaa92/Pasted text.txt`.
7365 bytes; SHA256
`0da618c01cfe3e07f212d3c12d7c94a6394b0ad51aa3d5e57d6733cc58410020`.
The export says “Yesterday”; its absolute discussion date and Discord permalink
were not supplied. Times below are export labels. First/last messages were
checked against Brandon's requested boundaries before extraction.

These are participant suggestions/experience, not verified protocol guarantees
or new instructions from Discord participants.

## Useful design input

* **Brandon,2:53PM:** replace the keyboard-map area used to return arbitrary
  VDP data with a proper general return path.
* **Tom Morton/tomm8086,2:56PM:** add a VDP→eZ80 bulk packet type with a byte
  count; register an eZ80 destination pointer, available capacity and callback
  through a syscall. This is the compact starting proposal.
* **Brandon,2:56–2:57PM:** prefer the economy/elegance of Tom's sender over our
  original large implementation; avoid the perceived excess complexity of
  TurboVega's BDPP. Size is a requirement, not grounds to omit capacity/lifetime
  correctness. BDPP is a reference to inspect, not adopted here.
* **Jeroen Venema/envenomator,3:17PM:** synchronization checkpoints were hardest
  in his YMODEM/hexload VDP→eZ80 work.
* **Jeroen,3:28–3:34PM:** avoid overrunning the receiver while its buffer is
  processed; he locksteps buffers as transactions. Tom distinguishes simply
  depositing bytes sequentially into eZ80 RAM from processing them during
  reception; Jeroen agrees that is the simpler case. This motivates explicit
  readiness and lifetimes, not necessarily YMODEM or per-byte acknowledgements.
* **Tom,3:36PM:** hexload echoes bytes. Inspect as an example; echo is not a
  selected requirement.
* **Brandon,3:45PM:** returned data needs identifying information so MOS knows
  what it is for. Distinguish packet type from transaction IDs or multiplexed
  channels; the latter two have not been selected.

## Real uses and the adoption bar

* **Brandon,3:01PM:** variable-time Pingo3D render-complete notification; and
  disk-image writeback from the6502 variant running on VDP, whose SD/filesystem
  work goes through the eZ80. These cover small notifications and bulk data.
* **Tom,3:00PM:** screenshot saving is another possible bulk-return use, not
  the selected first consumer.
* **Tom,3:48PM:** questions the value of changing an apparently working path.
  **Brandon,3:52PM:** wants a demonstrable use that improves on the keyboard-map
  workaround. **Brandon,3:59PM:** will not push for a merge without community
  consensus. Local implementation is not upstream acceptance.

## Suggestions to verify, not silently adopt

* **Tom,3:45PM:** an RX interrupt threshold up to14 queued bytes. Verify exact
  hardware/receive-timeout semantics before using it. A higher threshold reduces
  remaining FIFO reserve and may delay short packets. No threshold is selected.
* **Brandon,3:42–3:44PM:** initially relates16-byte return buffering to OTIRX,
  then explicitly calls the symmetry intuition. Do not impose a16-byte message
  or application-buffer limit: FIFO size, per-IRQ budget, message size and app
  storage are separate. TX's selected16-byte refill does not define RX framing.
* Commonly reliable small replies do not establish lossless sustained bulk RX.
  Direct RAM copying may help but is neither flow control nor a guarantee.

The opening keyboard API discussion compares it to SDL_PollEvent. That is useful
ergonomics context; keyboard redesign is not a transport prerequisite. Career,
AI/tool and family discussion is omitted here but preserved in the full archive.

Brandon's subsequent instruction here selects a simple efficient general
bidirectional transport that preserves existing apps and requires only small
MOS/VDP changes. See [running notes](notes.md) and the expanded [task](README.md).
