# Research cost accounting — accepted development episodes

27 October 2026. These figures summarize the actual launcher records for 162 accepted episodes. Each method has 18 episodes and 360 budgeted queries; the full package therefore contains **3,240 budgeted queries**. Initialization/scorer work and other uninstrumented oracle activity are not completely counted. Do not label 3,240 as every oracle invocation made during development.

| Method | Mean driver minutes / episode | Sum of driver hours | Recorded machine context |
| --- | ---: | ---: | --- |
| Random | 15.99 | 4.80 | Linux GitHub CPU runners: runnervm8k3b6, runnervmxehtw |
| Chemeleon | 234.31 | 70.29 | Linux GitHub CPU runners: runnervm8k3b6, runnervmxehtw |
| Full | 5.22 | 1.57 | macOS ARM CPU: LiLinghaodeMacBook-Air.local |
| Routing OFF | 14.49 | 4.35 | Linux GitHub CPU runners: runnervmtai0g |
| Memory OFF | 5.33 | 1.60 | macOS ARM CPU: MacBook-Air.local |
| Exploration OFF | 34.71 | 10.41 | Windows CPU: Wander-Lust |
| M3 full | 11.40 | 3.42 | Windows CPU: DESKTOP-I5OMH5V |
| M3 planning OFF | 7.18 | 2.16 | Windows CPU: DESKTOP-I5OMH5V |
| M3 self-correction OFF | 11.24 | 3.37 | Windows CPU: DESKTOP-I5OMH5V |

The summed accepted-episode launcher time is 101.96 hours. Parallel runs overlap: this sum is neither elapsed campaign time nor CPU-hours. A method mean weights its 18 episodes equally, equivalent here to equal system weights within each of the three seeds. The companion [CSV](method_cost_summary.csv) also records sample SD across seed-mean times, ranges, exact platforms/processors and every reported hostname.

All 162 records report USD 0 in known fees. This means the measured oracle/model/API components have no recorded unit price; it does **not** mean free or fully priced computation. Original baseline metadata labels its cost accounting “complete”; the other methods label it “partial”. Those labels are preserved in the CSV, while this report retains the broader missing-cost boundary for every method. Hardware, electricity, failed/interrupted work, setup and other unpriced activity are not fully monetized. No new dollar estimate is substituted.

Input/output token counts and LLM dollar usage are unreported in these records. Their missing values remain blank rather than zero. The accepted-episode time sums omit failed attempts and installation/job overhead; preserved failed attempts remain available separately and are not converted into successful scores.

The Linux runners, macOS ARM references and Windows PCs have different hardware, dependencies, concurrency and workloads. These descriptive times do not isolate the runtime effect of routing, memory or exploration. No hardware speedup is inferred.

Cost inputs are [per_run_costs.csv](../results/per_run_costs.csv), read without changing metadata. SHA-256 of that source: `26a71fa774f85e9682ca9842b63b443eded03429544b27e006ab907fcd7df296`. No model/oracle calls were made to build this summary.
