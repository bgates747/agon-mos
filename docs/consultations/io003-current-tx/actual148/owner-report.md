# Combined async UART0 and disk-saving qualification

The corrected eZ80-hosted app passes the complete Olimex functional test:
async display, real keyboard controls, disk saving, clean quit and loading the
saved program in a fresh app session. Console8 deployment still awaits exact
bench restoration and normal release. Sound is disabled; this is not a speed
benchmark or Console8 human acceptance.

1. **Identity.** Actual148, request429d91d688fd, frozen d3c7feaf kit,
   EMOSa25f and nativeF6f2c083e1. The app is a07ef5c9 with the observed-character
   Control-] correction. Other linked core, renderer, codec and transport
   objects are retained. The separately guarded bare-RC3 C8 app is cf4b881e.
2. **Execution.** One foreground invocation after the fresh joined/stopped
   owner handoff. All26 inputs copied and fully read back. Four phases executed
   once: synchronous pixel probe, async pixel probe, save, fresh reload.
   Parent-written supervisor wait0, reader0, all23 owned groups independently
   absent and key journals terminal. Consumer duration353.388693 seconds includes
   transfers, diagnostics and checks; it is not an application performance cost.
3. **Display.** Both independent MAME-derived pixel probes pass, including
   sparse/phase-only rows, green/color changes, mixed text, artwork and invalid
   packet handling. The async probe accepts/completes one423-byte packet.
4. **Playable save and controls.** Real input enters the five-line ASYNCIO
   program, saves, clears, loads and runs it, producing8675309 and7123456.
   Both drive choosers/cancel/state restoration and color0/1 pass. Control-]
   with actual ASCII93/virtual-key107 returns cleanly. Twenty accepted async
   packets totaling9237 bytes complete before exit.
5. **Fresh reload.** A new invocation opens the written image, loads/runs
   ASYNCIO, produces both outputs and quits. Twenty packets totaling16058 bytes
   complete. Both saved app states show mode1, callback/route0, no dirty tracks,
   color1, enabled/idle transport and no error.
6. **Independent persistence oracle.** Every WOZ track decodes, ASYNCIO's58
   tokenized program bytes equal returned guest RAM in both sessions, and only
   permitted track/CRC bytes change. The166 changed bytes preserve unrelated
   metadata. Both returned images hash0487a55d. Original146's failure remains
   unchanged; this is a separately frozen corrected run.
7. **Restoration and deployment.** Stopped custody returned to Extender in
   consumer-stopped-return.json at22:19:43UTC; mail23 and immediate Steer delivered.
   Exact native-prefix-first restoration, fresh full handback and normal release
   are pending. The local C8 package is not deployed or ready for human review
   until those gates pass. Preserve all existing user disk images.
8. **Limits.** This proves the selected instrumented functionality and observed
   fit, not peak heap/stack, every optical frame, audio or uninstrumented speed.
   Incremental/fixed388ef52 cumulative and native-game performance comparisons
   are unavailable. Bare RC3 and EMOS have separately guarded completion
   contracts; Olimex qualification does not substitute for C8 manual review.

Evidence is in build/io003/playable-quit-physical-r01: original-actor.json,
actual-supervisor.json, actual/reader.json, actual/serial.log, actual/summary.json,
all four original oracle receipts and consumer-stopped-return.json.
qualification.json retains restoration/release gates explicitly.
