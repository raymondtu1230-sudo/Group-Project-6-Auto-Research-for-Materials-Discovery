# Recorded time and partial costs

198 accepted dev episodes contain 3,960 budgeted queries. This is not a total project-resource count: initialization, failed or incomplete attempts and uninstrumented work remain outside the successful-episode query count.

| Method | Recorded launcher minutes / episode | Platform |
| --- | ---: | --- |
| Random | 15.99 | Linux-6.17.0-1022-azure-x86_64-with-glibc2.39; Linux-7.0.0-1017-azure-x86_64-with-glibc2.39 |
| Chemeleon | 234.31 | Linux-6.17.0-1022-azure-x86_64-with-glibc2.39; Linux-7.0.0-1017-azure-x86_64-with-glibc2.39 |
| Frozen Full | 5.22 | macOS-26.3-arm64-arm-64bit |
| Planning OFF | 5.56 | Windows-11-10.0.26300-SP0 |
| Memory OFF | 5.33 | macOS-26.6.2-arm64-arm-64bit |
| Self-correction OFF | 14.41 | Windows-11-10.0.26300-SP0 |
| Exploration OFF | 34.71 | Windows-11-10.0.26200-SP0 |
| Routing OFF | 14.49 | Linux-6.17.0-1022-azure-x86_64-with-glibc2.39 |
| M3 full | 11.40 | Windows-11-10.0.26300-SP0 |
| M3 planning OFF | 7.18 | Windows-11-10.0.26300-SP0 |
| M3 self-correction OFF | 11.24 | Windows-11-10.0.26300-SP0 |

These are recorded launcher times on different machines, operating systems and execution schedules. They are descriptive accounting, not a controlled speed ranking. New M3 planning OFF averages 5.56 minutes and self-correction OFF 14.41 minutes on the reported Windows host; Full's reference comes from the recorded macOS machine. Do not attribute the time difference solely to the module switch.

Known recorded model fees sum to USD 0. Unknown hardware, electricity, unpriced attempts and missing LLM/token counters remain unknown; they are not imputed as zero. The complete [machine-labelled table](method_cost_summary.csv) and [individual records](../results/per_run_costs.csv) retain the measurement scope. Published platform descriptions replace host names; original metadata remains at its source.
