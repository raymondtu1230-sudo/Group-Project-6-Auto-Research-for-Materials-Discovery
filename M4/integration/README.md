# Deferred M1 integration

The main-branch handoff adds only M4/ and leaves M1 unchanged.

This directory retains the M1 configuration example and integration test used in earlier validation. They are references for later adoption and are not loaded automatically. Once M1/M3 agree on integration, apply the relevant memory_manager block and test to M1. Do not overwrite a newer configuration with the entire saved example.

The main-branch M1 memory_manager setting remains unchanged. The 34-test integration result and real ORB run used the earlier temporary wiring; they do not mean M4 is enabled in the current main agent. Run standalone tests using M4/README.md.
