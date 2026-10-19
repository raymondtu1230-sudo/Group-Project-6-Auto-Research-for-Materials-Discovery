# New exact-data recovery diagnostic, not production admission

The failed run39286986254 remains failed under its original gate. Its GitHub job records show runner42 (interrupt), runner41 (continuous), runner48 (resume), despite repeated hostnames. The hostname inequality check was not a valid runner identity check.

The new fixture retains all original CIF files and exact serialized ASE sample fingerprints from continuous (no replay, two original sample calls) and interrupted/resumed paths, with both batch and final RNG hashes. Acceptance requires exact ordered CIF bytes and exact sampled atom data/identity/RNG, all512 candidates, unchanged256 diffusion steps and batch256, no duplicated first batch, matching source, and distinct runner and job IDs confirmed against retained GitHub jobs metadata. No numeric rounding or tolerance is introduced. Full pymatgen dictionary equality and hostnames stay visible as diagnostics; their last-bit derived values cannot replace exact independent-data evidence. Only output locations/observability differ from the original generator. The scientific generator/model source is unchanged.

This uses Li2O512 as a diagnostic fixture, not a dev/check baseline score or a complete1024-pool production-wrapper proof. Formal Chemeleon17 remains blocked until the necessary later admission checks. No original accepted unit is rerun.

Preservation also now uses SHA256-addressed extraction and a separate immutable original-pair manifest, avoiding duplicate imports as the full reusable manifest grows. Further captures preserve existing raw units, not new experiments.
