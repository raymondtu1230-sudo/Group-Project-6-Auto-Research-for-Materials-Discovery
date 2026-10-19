# Preparation only — awaiting colleague reply

At 20 October 2026 01:03 Asia/Singapore, the user asked for a short M2-only reply and authorized preparation while waiting for the colleague's response before confirming the check execution arrangement.

`M2/prepare_split.py` reads the unchanged formal protocol and system files without API calls. It actually produced the four check systems × three official seeds = 12 Chemeleon matrix entries, B=20, in `M2/configs/check-baselines-preparation.json`. The new script passed Ruff. The workflow source in `M2/workflows/m2-split-preparation.yml` is a preparation-only template, not installed as an active workflow; it has dev/check/hidden input choices but starts no scientific jobs. Hidden availability and driver support remain M1/evaluation dependencies. The existing scientific workflow has not yet been converted to production multi-split dispatch.

No check/hidden experiment has been launched. Confirm the arrangement after the colleague replies; verify recovery or adequate runtime capacity, then validate one Chemeleon check unit before considering the other eleven. Existing missing-only dev Random jobs continue. M1 ownership is unchanged.
