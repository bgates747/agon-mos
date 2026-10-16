# Shared MOS extension reservations

The foundation's main branch owns shared identifier reservations. Custom MOS
implementations live in their own projects, not special branches here. The
register does not enable UART or qsort in stock firmware.

`reservations.json` is the sole local extension allocation authority. Namespace,
value, owner, purpose, status and discovery ABI are recorded together. The
generated bindings are `src/mos_api_reservations.inc` and
`api/include/mos_api_reservations.h`; do not edit them independently.

1. Getfunction `0x13` is reserved for `agon-mos`'s experimental
   `mos_function_uart0_async` / `MOS_FUNCTION_UART0_ASYNC`. Use existing RST08
   call `mos_getfunction` (`0x50`), B=index and C=0. Check A=0 and HL!=0, then
   call that returned discovery function to obtain the UTX1 table. It is not
   already a table pointer. Require compatible magic/version/length/flags;
   otherwise retain synchronous fallback. ABI1.2's table is at least 54 bytes.
2. Getfunction `0x12` is a retired qsort tombstone, unavailable for reuse.
   No callable qsort constant is exported and no qsort implementation is added.
3. No new RST08 identifier or extra range is allocated. UART adds operations
   inside its versioned table; it must return for review before expanding its
   global allocation or changing the discovery contract.

These are local family reservations, not official upstream allocations. The
selected official v3.0.2 table and the
[upstream main table checked on 2026-10-16](https://github.com/AgonPlatform/agon-mos/blob/main/src/mos_api.asm)
end at `0x11`. Future upstream imports require another collision audit; a local
reservation cannot prevent upstream from assigning the same index.

## Consuming the canonical interfaces

Assembly consumes the foundation's `src/mos_api.inc`, which imports the generated
reservation include. Select this shared include directory, rather than a
private replacement `mos_api.inc`. Additional assembler dialects need generated,
checked bindings, not independently assigned values.

C/C++ code continues to include `<agon/mos.h>`. Put this package's `api/include`
before the selected AgonDev SDK include directory. Its small canonical overlay
uses `#include_next` to import the SDK's unmodified declarations, then adds the
generated extension constants. No SDK header is copied or edited. The UART
operations are an ADL register ABI: these constants do not manufacture C-callable
function-pointer declarations or wrappers.

`MOS_EXTENSION_API_REVISION` and `MOS_EXTENSION_API_SHA256` identify the interface
register, **not firmware version or runtime capability**. Pin the shared
dependency revision and consumed file hashes in custom-build provenance.
Use the committed shared dependency selected in the owner handoff; record dirty
status/content hashes when deliberately testing later local modifications.
Full banner/firmware-commit metadata generation remains separate API-001 work.

From the foundation root, with the selected helper dependency:

```bash
make api-check MOS_AGONDEV_ROOT=../mos-agondev
```

After an owner-reviewed register edit, regenerate through the selected helper's
`scripts/generate_api_reservations.py --source-root .`, then run `api-check`.
Normal root firmware/baseline targets check bindings before compilation.
The check rejects duplicate identifiers, wrong namespaces, stale bindings and
conflicting getfunction table entries. Only the owning custom project supplies
its implementation/table slot and performs feature-specific qualification.
