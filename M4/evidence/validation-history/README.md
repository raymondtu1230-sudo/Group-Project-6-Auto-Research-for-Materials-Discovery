# Historical validation output

- `test_results.txt`: earlier validation, 36 passed and 1 deselected.
- `joint_test_results.txt`: 21 October joint validation, 69 passed.

These original logs retain their original counts. The final 26 October relevant suite passed all 72 tests. See [current validation](../../VALIDATION.md) and [the final validation record](../frozen-memory-ablation-20261026/closeout_validation.json).

- `20261027-72-tests.txt`: fresh local complete-environment rerun, 72 passed, 3 existing dependency warnings. M2 had validated the 15 standalone tests but could not collect the 72-test suite in its lighter environment; this local log preserves the distinction.
