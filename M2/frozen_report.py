"""Report preserved real M2 ablations and the frozen M1 final metrics.

No models, agents, datasets, or oracles are invoked.  The reporter only reads
the original outputs and the collection/validation evidence saved after runs.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import html
import json
import math
import statistics
from pathlib import Path
from typing import Any

METHOD = "tool_routing_off"
REFERENCE = "m1_full"
COMMIT = "02e0026bf450f71f4f7862228d295f5b02b49e12"
SYSTEMS = ("Mg-Sn-Sr", "Au-K-Tb", "Co-Mg-Na", "Hf-Ni-Zr", "Co-Dy-W", "Ga-Pt-Tm")
SEEDS = (17, 29, 43)
MSUN = "novelty_stable_unique_novel_count"
CURVE = "num_newly_discovered_stable"
AUDC = "final/discovery_curve_area_under_discovery_curve"
EXPECTED = {(system, seed) for system in SYSTEMS for seed in SEEDS}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )


def snapshot_hash(entries: list[dict[str, Any]]) -> str:
    """Use the same independent-data canonicalization as M2/evaluate.py."""
    canonical = copy.deepcopy(entries)
    for entry in canonical:
        attribute = entry.get("attribute")
        structure = attribute.get("structure") if isinstance(attribute, dict) else None
        if not isinstance(structure, dict):
            continue
        lattice = structure.get("lattice", {})
        if "matrix" in lattice:
            for field in ("a", "b", "c", "alpha", "beta", "gamma", "volume"):
                lattice.pop(field, None)
        for site in structure.get("sites", []):
            if "matrix" in lattice and "abc" in site:
                site.pop("xyz", None)
    values = sorted(
        json.dumps(x, sort_keys=True, separators=(",", ":")) for x in canonical
    )
    return hashlib.sha256("\n".join(values).encode()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def label(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_runs(
    root: Path, method: str, own: bool
) -> tuple[
    dict[tuple[str, int], dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    accepted: dict[tuple[str, int], dict[str, Any]] = {}
    failures: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for path in sorted(root.rglob("run_metadata.json")):
        directory = path.parent
        source = label(directory, root)
        try:
            metadata = read_json(path)
            if metadata.get("method") != method or metadata.get("split") != "dev":
                continue
            system, seed = "-".join(metadata["system"]), metadata["seed"]
            key = (system, seed)
            if key not in EXPECTED:
                raise ValueError("Unexpected dev system/seed")
            if metadata.get("status") != "completed":
                failures.append(
                    {
                        "method": method,
                        "system": system,
                        "seed": seed,
                        "attempt": metadata.get("attempt"),
                        "status": metadata.get("status"),
                        "error": metadata.get("error"),
                        "source": source,
                    }
                )
                continue
            if metadata.get("query_budget") != 20 or metadata.get("episodes") != 1:
                raise ValueError("Completed run does not use B20 and one episode")
            trajectory = read_json(directory / "trajectories/episode_000.json")
            summary = read_json(directory / "summary/summary.json")
            metrics = trajectory.get("metrics", {})
            if (
                len(trajectory.get("trajectory", [])) != 20
                or metrics.get("final/queries_used") != 20
            ):
                raise ValueError("Trajectory and final query count do not both equal20")
            if summary.get("episodes") != 1:
                raise ValueError("Summary does not contain one episode")
            for field in ("final/" + MSUN, AUDC):
                if not finite(metrics.get(field)):
                    raise ValueError(f"Nonfinite official final metric: {field}")
                summarized = summary.get("summary", {}).get(field, {}).get("mean")
                if summarized != metrics[field]:
                    raise ValueError(f"Summary/trajectory disagreement: {field}")
            reference = trajectory.get("phase_diagram_gt")
            if not isinstance(reference, list) or not reference:
                raise ValueError("Material reference snapshot missing")
            run = {
                "directory": directory,
                "source": source,
                "metadata": metadata,
                "trajectory": trajectory,
                "mSUN_at_20": metrics["final/" + MSUN],
                "AUDC": metrics[AUDC],
                "reference_hash": snapshot_hash(reference),
            }
            if own:
                validation = read_json(directory / "m2_validation.json")
                if validation.get("accepted") is not True or validation.get("errors"):
                    raise ValueError("Saved M2 audit did not accept this attempt")
                if (
                    validation.get("actual_git_head") != COMMIT
                    or validation.get("actual_tag_commit") != COMMIT
                ):
                    raise ValueError(
                        "Saved audit does not identify the required frozen commit/tag"
                    )
                if validation.get("tracked_worktree_clean") is not True:
                    raise ValueError("Saved tracked-worktree check was not clean")
                if (
                    validation.get("canonical_material_reference_sha256")
                    != run["reference_hash"]
                ):
                    raise ValueError(
                        "Persisted trajectory reference differs from accepted audit"
                    )
                collection = read_json(directory / "m2_collection.json")
                if (
                    collection.get("exit_code") != 0
                    or collection.get("collection_complete") is not True
                ):
                    raise ValueError("Process/collection did not finish successfully")
                if collection.get("original_metadata_sha256") != sha256(path):
                    raise ValueError("Original metadata integrity check failed")
                manifest = read_json(directory / "m2_sha256_manifest.json").get(
                    "files", {}
                )
                if not manifest:
                    raise ValueError("Preserved-file integrity manifest is empty")
                for relative, expected_sha in manifest.items():
                    file = directory / relative
                    if not file.is_file() or sha256(file) != expected_sha:
                        raise ValueError(f"Preserved-file SHA256 mismatch: {relative}")
                capture = read_json(directory / "m2_metrics_history.json")
                history = capture.get("metrics_history", [])
                if capture.get("complete_curve") is not True or [
                    x.get("queries_used") for x in history
                ] != list(range(1, 21)):
                    raise ValueError(
                        "Official saved history does not cover queries1..20"
                    )
                for point in history:
                    for field in (MSUN, CURVE):
                        if (
                            not finite(point.get(field))
                            or not 0 <= point[field] <= point["queries_used"]
                        ):
                            raise ValueError(
                                f"Invalid official history metric: {field}"
                            )
                if history[-1][MSUN] != run["mSUN_at_20"]:
                    raise ValueError("Saved official history/final mSUN mismatch")
                recomputed_audc = validation.get("official_audc_recomputed")
                if not finite(recomputed_audc) or not math.isclose(
                    recomputed_audc, run["AUDC"], rel_tol=1e-9, abs_tol=1e-9
                ):
                    raise ValueError(
                        "Saved official AUDC recomputation/final metric mismatch"
                    )
                run["history"] = history
            if key in accepted:
                raise ValueError(
                    "More than one accepted completed attempt for the same unit; deduplicate explicitly"
                )
            accepted[key] = run
        except Exception as error:
            issues.append(
                {
                    "method": method,
                    "source": source,
                    "error": f"{type(error).__name__}: {error}",
                }
            )
    return accepted, failures, issues


def costs(
    runs: dict[tuple[str, int], dict[str, Any]], method: str
) -> list[dict[str, Any]]:
    rows = []
    for (system, seed), run in sorted(runs.items()):
        metadata = run["metadata"]
        cost = metadata.get("cost", {})
        llm = cost.get("llm", {})
        rows.append(
            {
                "method": method,
                "system": system,
                "seed": seed,
                "attempt": metadata.get("attempt"),
                "oracle_queries": 20,
                "wall_time_seconds": metadata.get("wall_time_seconds"),
                "machine": metadata.get("machine"),
                "processor": metadata.get("processor"),
                "platform": metadata.get("platform"),
                "python": metadata.get("python"),
                "total_known_cost_usd": cost.get("total_known_cost_usd"),
                "recorded_total_cost_status": cost.get(
                    "total_cost_status", "not_reported"
                ),
                "report_cost_scope": "partial: hardware/electricity and unpriced failed attempts excluded",
                "llm_calls": llm.get("calls"),
                "llm_input_tokens": llm.get("input_tokens"),
                "llm_output_tokens": llm.get("output_tokens"),
                "llm_cost_usd": llm.get("cost_usd"),
                "source": run["source"],
            }
        )
    return rows


def curve_svg(runs: dict[tuple[str, int], dict[str, Any]], destination: Path) -> None:
    """Plot actual saved official M2 history; no missing M1 curve is invented."""
    width, height = 1220, 1920
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        "<style>text{font-family:Arial,sans-serif;fill:#17243b}.axis{stroke:#34425a;stroke-width:1}.grid{stroke:#e5eaf2;stroke-width:1}</style>",
        '<text x="65" y="38" font-size="24" font-weight="bold">M2 tool_routing_off: official development discovery curves</text>',
        '<text x="65" y="64" font-size="14">Mean ± sample SD across the three seeds; each point comes from the saved official query history.</text>',
    ]
    for row, system in enumerate(SYSTEMS):
        group = [runs[(system, seed)] for seed in SEEDS if (system, seed) in runs]
        for column, metric in enumerate((MSUN, CURVE)):
            left, top, plot_w, plot_h = 75 + column * 600, 125 + row * 285, 490, 190
            title = "mSUN" if metric == MSUN else "Official AUDC-source count"
            parts.append(
                f'<text x="{left}" y="{top - 20}" font-size="16" font-weight="bold">{html.escape(system)} · {title} (n={len(group)})</text>'
            )
            for tick in (0, 5, 10, 15, 20):
                x, y = left + plot_w * tick / 20, top + plot_h * (1 - tick / 20)
                parts.extend(
                    [
                        f'<line x1="{left}" y1="{y}" x2="{left + plot_w}" y2="{y}" class="grid"/>',
                        f'<text x="{left - 12}" y="{y + 4}" text-anchor="end" font-size="12">{tick}</text>',
                        f'<text x="{x}" y="{top + plot_h + 20}" text-anchor="middle" font-size="12">{tick}</text>',
                    ]
                )
            parts.extend(
                [
                    f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" class="axis"/>',
                    f'<line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" class="axis"/>',
                    f'<text x="{left + plot_w / 2}" y="{top + plot_h + 42}" text-anchor="middle" font-size="13">Oracle queries</text>',
                ]
            )
            if not group:
                continue
            histories = [
                [0, *[point[metric] for point in run["history"]]] for run in group
            ]
            means = [statistics.mean(values) for values in zip(*histories, strict=True)]
            deviations = [
                statistics.stdev(values) if len(values) > 1 else 0
                for values in zip(*histories, strict=True)
            ]

            def point(
                index: int,
                value: float,
                left=left,
                top=top,
                plot_w=plot_w,
                plot_h=plot_h,
            ) -> str:
                return f"{left + plot_w * index / 20:.2f},{top + plot_h * (1 - value / 20):.2f}"

            upper = [point(i, min(20, means[i] + deviations[i])) for i in range(21)]
            lower = [
                point(i, max(0, means[i] - deviations[i])) for i in reversed(range(21))
            ]
            parts.append(
                f'<polygon points="{" ".join(upper + lower)}" fill="#246ac8" fill-opacity="0.16"/>'
            )
            line = " ".join(point(i, value) for i, value in enumerate(means))
            parts.append(
                f'<polyline points="{line}" fill="none" stroke="#246ac8" stroke-width="2.6"/>'
            )
    parts.extend(
        [
            '<text x="65" y="1870" font-size="14">M1 reference curves are omitted because the frozen reference lacks original per-query history attachments.</text>',
            '<text x="65" y="1895" font-size="13">The zero-query discovery count is zero by protocol. Shading is clipped to the feasible count range [0,20].</text>',
            "</svg>",
        ]
    )
    destination.write_text("\n".join(parts))


def report(results_root: Path, reference_root: Path, output: Path) -> dict[str, Any]:
    if output.exists() and any(output.iterdir()):
        raise ValueError(
            "Report directory already contains files; choose a new directory"
        )
    own, failed, issues = load_runs(results_root, METHOD, True)
    reference, reference_failed, reference_issues = load_runs(
        reference_root, REFERENCE, False
    )
    issues.extend(reference_issues)
    paired = []
    missing_audit = []
    for key in sorted(EXPECTED & set(reference)):
        run = reference[key]
        missing = [
            name
            for name in (
                "resolved_config.yaml",
                ".hydra/config.yaml",
                "m2_metrics_history.json",
                "m4_evidence.jsonl",
                "m5_decisions.jsonl",
            )
            if not (run["directory"] / name).is_file()
        ]
        if missing:
            missing_audit.append(
                {
                    "system": key[0],
                    "seed": key[1],
                    "source": run["source"],
                    "missing": missing,
                }
            )
    for (system, seed), run in sorted(own.items()):
        baseline = reference.get((system, seed))
        pair_valid = baseline is not None
        if baseline is not None:
            for field in ("protocol_settings", "m1_input_sha256"):
                if run["metadata"].get(field) != baseline["metadata"].get(field):
                    issues.append(
                        {
                            "method": METHOD,
                            "system": system,
                            "seed": seed,
                            "error": f"Paired frozen-reference {field} mismatch",
                        }
                    )
                    pair_valid = False
            if run["reference_hash"] != baseline["reference_hash"]:
                issues.append(
                    {
                        "method": METHOD,
                        "system": system,
                        "seed": seed,
                        "error": "Paired material-reference revision differs",
                    }
                )
                pair_valid = False
        metadata = run["metadata"]
        paired.append(
            {
                "system": system,
                "seed": seed,
                "method": METHOD,
                "attempt": metadata.get("attempt"),
                "B": 20,
                "oracle_queries": 20,
                "mSUN_at_20": run["mSUN_at_20"],
                "AUDC": run["AUDC"],
                "m1_full_mSUN_at_20": baseline["mSUN_at_20"] if pair_valid else None,
                "m1_full_AUDC": baseline["AUDC"] if pair_valid else None,
                "delta_mSUN_off_minus_full": run["mSUN_at_20"] - baseline["mSUN_at_20"]
                if pair_valid
                else None,
                "delta_AUDC_off_minus_full": run["AUDC"] - baseline["AUDC"]
                if pair_valid
                else None,
                "pair_status": "matched_system_seed_budget_protocol_inputs_material_reference"
                if pair_valid
                else "missing_or_incompatible_reference",
                "wall_time_seconds": metadata.get("wall_time_seconds"),
                "machine": metadata.get("machine"),
                "canonical_material_reference_sha256": run["reference_hash"],
                "source": run["source"],
                "m1_reference_source": baseline["source"] if baseline else None,
            }
        )
    missing_own = sorted(EXPECTED - set(own))
    missing_reference = sorted(EXPECTED - set(reference))
    complete = (
        not missing_own
        and not missing_reference
        and not issues
        and len(paired) == 18
        and all(row["pair_status"].startswith("matched_") for row in paired)
    )
    audit = {
        "frozen_commit": COMMIT,
        "split": "dev",
        "method": METHOD,
        "expected_unique_units": 18,
        "accepted_unique_units": len(own),
        "reference_unique_units": len(reference),
        "missing_own_units": missing_own,
        "missing_reference_units": missing_reference,
        "issues": issues,
        "own_failed_attempts_preserved": len(failed),
        "reference_failed_attempts_preserved": len(reference_failed),
        "complete_paired_final_metric_comparison": complete,
        "m1_missing_original_audit_attachments": missing_audit,
        "m1_missing_attachments_block_final_metric_pairing": False,
        "m1_full_curves_and_AF_EF": "not computed: original per-query history unavailable",
        "independent_baseline_comparisons": "not computed: baseline raw runs not supplied to this reporter",
        "aggregation": "six equally weighted systems within each seed; mean and sample SD across the three seed means",
        "cost_scope": "Recorded known fees only; hardware, electricity and all unpriced failed attempts remain excluded.",
    }
    seed_rows, summaries = [], []
    fields = {
        METHOD: ("mSUN_at_20", "AUDC"),
        REFERENCE: ("m1_full_mSUN_at_20", "m1_full_AUDC"),
        "paired_delta_off_minus_full": (
            "delta_mSUN_off_minus_full",
            "delta_AUDC_off_minus_full",
        ),
    }
    for method, (msun_field, audc_field) in fields.items():
        group_rows = []
        for seed in SEEDS:
            units = [row for row in paired if row["seed"] == seed]
            valid = (
                not issues
                and len(units) == 6
                and all(
                    finite(row.get(msun_field)) and finite(row.get(audc_field))
                    for row in units
                )
            )
            row = {
                "method": method,
                "seed": seed,
                "systems_available": len(units),
                "systems_expected": 6,
                "complete_seed": valid,
                "mSUN_at_20_mean": statistics.mean(x[msun_field] for x in units)
                if valid
                else None,
                "AUDC_mean": statistics.mean(x[audc_field] for x in units)
                if valid
                else None,
            }
            seed_rows.append(row)
            group_rows.append(row)
        valid = all(row["complete_seed"] for row in group_rows)
        summaries.append(
            {
                "method": method,
                "complete_18_unit_sweep": valid,
                "seed_n": sum(row["complete_seed"] for row in group_rows),
                "units_expected": 18,
                "mSUN_at_20_mean": statistics.mean(
                    row["mSUN_at_20_mean"] for row in group_rows
                )
                if valid
                else None,
                "mSUN_at_20_seed_sample_SD": statistics.stdev(
                    row["mSUN_at_20_mean"] for row in group_rows
                )
                if valid
                else None,
                "AUDC_mean": statistics.mean(row["AUDC_mean"] for row in group_rows)
                if valid
                else None,
                "AUDC_seed_sample_SD": statistics.stdev(
                    row["AUDC_mean"] for row in group_rows
                )
                if valid
                else None,
            }
        )
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "perunit.csv", paired)
    write_csv(output / "seed_aggregate.csv", seed_rows)
    write_csv(output / "method_summary.csv", summaries)
    write_csv(output / "costs.csv", costs(own, METHOD) + costs(reference, REFERENCE))
    (output / "validation.json").write_text(
        json.dumps(audit, indent=2, allow_nan=False) + "\n"
    )
    (output / "failed_attempts.json").write_text(
        json.dumps(failed + reference_failed, indent=2, allow_nan=False) + "\n"
    )
    curve_svg(own, output / "official_curves.svg")
    rows = [
        "| Method | mSUN@20 mean ± seed SD | AUDC mean ± seed SD |",
        "| --- | --- | --- |",
    ]
    for summary in summaries:
        if summary["complete_18_unit_sweep"]:
            rows.append(
                f"| {summary['method']} | {summary['mSUN_at_20_mean']:.4f} ± {summary['mSUN_at_20_seed_sample_SD']:.4f} | {summary['AUDC_mean']:.4f} ± {summary['AUDC_seed_sample_SD']:.4f} |"
            )
        else:
            rows.append(f"| {summary['method']} | incomplete | incomplete |")
    text = f"""# M2 frozen development tool-routing ablation

Frozen source: `{COMMIT}` (`m1-freeze-20261025`). Accepted M2 units: {len(own)}/18.
Complete paired final-metric comparison: {complete}.

All reported discovery values come from actual preserved official trajectories,
summaries and checkpoint metric histories. This reporter invokes no agent,
model, oracle, Materials Project request or simulated experiment.

{chr(10).join(rows)}

Each seed mean gives the six systems equal weight. The final mean and sample
standard deviation are calculated across the three seed means, not across18
independent seeds. Delta is `tool_routing_off - m1_full`; positive values favor
the routing-off condition and negative values favor full routing.

`perunit.csv` contains the paired final scores and differences. `seed_aggregate.csv`
and `method_summary.csv` expose the aggregation. `official_curves.svg` plots only
M2's actual saved per-query histories; mSUN and the official AUDC-source count
are distinct metrics. The SHA256 manifests and raw complete attempt directories
remain the evidence source; report CSV files do not replace those directories.

## M1 reference audit attachments

{len(missing_audit)} reference units lack one or more original Hydra/resolved
configuration, component-log or per-query-history attachments in the supplied
frozen result tree. The missing-file list is in `validation.json`. Final metric
pairing uses the actual official final trajectory/summary values after checking
system, seed, B, protocol, scientific input hashes and canonical material
reference identity. Missing M1 attachments have not been invented or re-labelled
as originals. M1 discovery curves and AF/EF are consequently not reported here.
The original M1 attachments should be supplied separately for the complete audit.

The previously completed Random/Chemeleon baseline results are not re-run or
assumed compatible by this script. Their raw evidence was not an input to this
report, so no new AF/EF or baseline pairing is claimed.

## Cost and failed attempts

`costs.csv` records each method's machine, CPU/OS, elapsed driver time, query
count and known fee fields. A recorded USD0 model fee is not zero total cost.
Hardware, electricity and all unpriced failed attempts remain outside those
fees; unknown LLM calls/tokens stay blank. Different machines are not treated as
a controlled hardware-speed comparison. `failed_attempts.json` indexes preserved
failed attempts. No failed attempt was deleted or used as a completed score.

Input roots:
- M2: `{results_root}`
- Frozen M1 reference: `{reference_root}`
"""
    (output / "README.md").write_text(text)
    return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-root", type=Path, required=True)
    parser.add_argument("--reference-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit = report(
        args.results_root.resolve(),
        args.reference_root.resolve(),
        args.output.resolve(),
    )
    print(
        json.dumps(
            {
                "accepted_unique_units": audit["accepted_unique_units"],
                "reference_unique_units": audit["reference_unique_units"],
                "complete": audit["complete_paired_final_metric_comparison"],
                "output": str(args.output),
            }
        )
    )
    if not audit["complete_paired_final_metric_comparison"]:
        raise SystemExit(
            "Incomplete or inconsistent result set; inspect validation.json"
        )


if __name__ == "__main__":
    main()
