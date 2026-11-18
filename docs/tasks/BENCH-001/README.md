# BENCH-001 — Consolidate Olimex bench procedure references

Status: complete. Requested by Brandon on November 17, 2026.

## Objective and authority

Make the [Extender bench guide](../../../../agon-extender/docs/operations/olimex-bench/README.md)
the sole authoritative reference for physical Olimex bench procedures. Remove
contrary local instructions entirely, including obsolete historical procedural
text and cached/generated document copies. A warning or superseded banner is
not a substitute for removing the conflicting instructions.

This task changes local project documentation only. It does not reserve a slot,
access hardware, run a fixture, edit shared scheduling state, change firmware,
modify boot scripts, or commission new test implementation. Product/source
ownership, test-specific inputs and expected results remain distinct from bench
operation procedures. Oryx emulator and Pi compiler scheduling are separate.

## Plan

- [x] Read the canonical guide and identify procedural conflicts.
- [x] Inventory tracked and ignored local documentation, root agent/handoff
      files, test plans, copied mail, manifests and script documentation.
- [x] Replace local bench policy/runbook instructions with the canonical link;
      delete obsolete procedure-only documents or their conflicting sections.
- [x] Preserve result data and factual past observations. Remove instructions
      embedded in historical documents rather than keep a second runbook.
- [x] Record every changed/deleted file, audit scope and verification outcome
      in this silo without copying the removed procedures into it.
- [x] Repeat searches and inspect remaining hits. Verify links and changes;
      commit and push the documentation tranche.

## Audit decisions

Procedural copies in machine-readable documents are documentation too. Historical
artifact hashes and result receipts remain evidence of their original runs;
editing or removing a linked procedural document does not silently regenerate
those past hashes. Any such documentation sanitation is recorded explicitly.
Existing archived binaries and program source are not commissioned for execution
by this task. Runtime code changes are outside this documentation request.

## Evidence and completion

The audit inventory, change ledger and completion report will be retained here.
The canonical guide itself is referenced, not copied. Git retains prior versions;
no local archive of removed conflicting procedures will be created.

## Completion report

Removed the obsolete lease-based runbooks, Extender-operated installation and
handoff instructions, fixed custody budgets, and historical snapshot restoration
requirements from local procedural text. Procedure-only pages now contain the
canonical link instead of a second procedure. Mixed task/results pages and copied
mail retain source contracts and factual results after their operating passages
were removed. Machine-readable preparation documents received the same treatment.

The audit covered root agent/ownership/handoff documents and recursive text
searches of docs, experiments and local build copies, including ignored files.
The candidate [inventory](INVENTORY.md) records 228 files (169 tracked, 59 local or
ignored); follow-up discoveries and every changed file are in [changes.json](changes.json).
One ignored duplicate grep dump was deleted. No replacement archive of obsolete
procedures was created. Git history retains prior tracked versions.

[Verification](verification.json) records parsed JSON, resolved canonical links
and confirmation that the RX006 driver's executable AST is unchanged. Diff
whitespace checks passed. No build, firmware, bench, boot-script or target action
was performed. Separate Console8 manual procedures, Pi compiler scheduling and
Oryx emulator scheduling remain separate workflows.

Historical artifact/source hashes describe their original snapshots. They were
not regenerated to disguise documentation changes; sanitized old plans are not
commissioned current jobs. Actual release/readback observations and binary/raw
results remain historical evidence, not present-day operating instructions.
