"""Summarize M3 ablation runs into CSV tables and the results section draft.

Reads completed protocol runs under ``M1/MADE/results/protocol_v1`` for
``m1_baseline`` and the three ``m3_*`` methods. When M1's baseline result
folders are not on this machine, ``M1/m1_baseline_dev_summary.csv`` supplies
the baseline mSUN and AUDC values.

Writes ``M3/results/m3_ablation_runs.csv``, ``M3/results/m3_ablation_summary.csv``
and ``M3/report/M3_RESULTS.md``. Uses only the Python standard library::

    python M3/summarize_ablations.py
"""

from __future__ import annotations

import csv
import json
import re
import statistics
from pathlib import Path
from typing import Any

M3_DIR = Path(__file__).resolve().parent
M1_DIR = M3_DIR.parent / "M1"
RESULTS = M1_DIR / "MADE" / "results" / "protocol_v1"
BASELINE_CSV = M1_DIR / "m1_baseline_dev_summary.csv"
METHODS = ("m1_baseline", "m3_full", "m3_planning_off", "m3_self_correction_off")
METRICS = {
    "msun": "final/novelty_stable_unique_novel_count",
    "msun_fraction": "final/novelty_stable_unique_novel_fraction",
    "audc": "final/discovery_curve_area_under_discovery_curve",
    "af": "final/discovery_curve_acceleration_factor",
    "ef": "final/discovery_curve_enhancement_factor",
}
# (treatment, control, what the difference measures)
COMPARISONS = (
    ("m3_full", "m1_baseline", "M3 (planner + self-correction) vs M1 reference"),
    ("m3_full", "m3_planning_off", "contribution of M3 planning"),
    ("m3_full", "m3_self_correction_off", "contribution of M3 self-correction"),
)
REPLAN = re.compile(r"M3 re-plan: .*reason=(\w+)")
REVIEW = re.compile(r"M3 review: ")
RUN_FIELDS = [
    "method",
    "system",
    "seed",
    *METRICS,
    "queries",
    "replans",
    "replans_no_progress",
    "replans_repetition",
    "reviews",
    "wall_time_seconds",
    "source",
]


def latest_completed(method_dir: Path) -> dict[tuple[str, int], Path]:
    runs: dict[tuple[str, int], Path] = {}
    for metadata in sorted(method_dir.glob("dev/*/seed_*/attempt_*/run_metadata.json")):
        if json.loads(metadata.read_text()).get("status") != "completed":
            continue
        attempt = metadata.parent
        system = attempt.parent.parent.name
        seed = int(attempt.parent.name.removeprefix("seed_"))
        runs[(system, seed)] = attempt  # sorted, so the latest attempt wins
    return runs


def read_run(method: str, system: str, seed: int, path: Path) -> dict[str, Any]:
    metadata = json.loads((path / "run_metadata.json").read_text())
    summary = json.loads((path / "summary" / "summary.json").read_text())["summary"]
    row: dict[str, Any] = {"method": method, "system": system, "seed": seed}
    for name, key in METRICS.items():
        value = summary.get(key, {}).get("mean")
        row[name] = float(value) if value is not None else None
    row["queries"] = metadata.get("cost", {}).get("oracle", {}).get("queries")
    row["wall_time_seconds"] = metadata.get("wall_time_seconds")
    # run_ablations.py saves the console beside the run (MADE empties
    # run_benchmark.log); read both so either source works.
    logs = [path.parent / f"console_{path.name}.log", *path.rglob("run_benchmark.log")]
    log_text = "".join(p.read_text(errors="ignore") for p in logs if p.is_file())
    reasons = REPLAN.findall(log_text)
    row["replans"] = len(reasons)
    row["replans_no_progress"] = reasons.count("no_progress")
    row["replans_repetition"] = reasons.count("repetition")
    row["reviews"] = len(REVIEW.findall(log_text))
    try:
        source = path.relative_to(M1_DIR.parent)
    except ValueError:  # results outside the repository
        source = path
    row["source"] = str(source).replace("\\", "/")
    return row


def baseline_from_csv(csv_path: Path) -> list[dict[str, Any]]:
    if not csv_path.is_file():
        return []
    rows = []
    with csv_path.open(newline="") as stream:
        for record in csv.DictReader(stream):
            rows.append(
                {
                    "method": "m1_baseline",
                    "system": record["system"],
                    "seed": int(record["seed"]),
                    "msun": float(record["msun_at_20"]),
                    "msun_fraction": float(record["msun_fraction"]),
                    "audc": float(record["audc"]),
                    "af": None,
                    "ef": None,
                    "queries": int(record["queries"]),
                    "wall_time_seconds": float(record["wall_time_seconds"]),
                    "source": csv_path.name,
                }
            )
    return rows


def collect(
    results: Path = RESULTS, baseline_csv: Path = BASELINE_CSV
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method in METHODS:
        for (system, seed), path in sorted(latest_completed(results / method).items()):
            rows.append(read_run(method, system, seed, path))
    have = {(r["system"], r["seed"]) for r in rows if r["method"] == "m1_baseline"}
    rows.extend(
        r
        for r in baseline_from_csv(baseline_csv)
        if (r["system"], r["seed"]) not in have
    )
    return rows


def _values(rows: list[dict[str, Any]], method: str, metric: str) -> list[float]:
    return [r[metric] for r in rows if r["method"] == method and r[metric] is not None]


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    table = []
    for method in METHODS:
        runs = [r for r in rows if r["method"] == method]
        if not runs:
            continue
        entry: dict[str, Any] = {"method": method, "runs": len(runs)}
        for metric in METRICS:
            values = _values(rows, method, metric)
            entry[f"{metric}_mean"] = statistics.fmean(values) if values else None
            entry[f"{metric}_std"] = (
                statistics.stdev(values) if len(values) > 1 else 0.0 if values else None
            )
        entry["replans_mean"] = (
            statistics.fmean(r.get("replans") or 0 for r in runs)
            if method != "m1_baseline"
            else None
        )
        table.append(entry)
    return table


def paired(
    rows: list[dict[str, Any]], treatment: str, control: str, metric: str = "msun"
) -> dict[str, Any] | None:
    a = {(r["system"], r["seed"]): r[metric] for r in rows if r["method"] == treatment}
    b = {(r["system"], r["seed"]): r[metric] for r in rows if r["method"] == control}
    keys = sorted(
        k for k in a.keys() & b.keys() if a[k] is not None and b[k] is not None
    )
    if not keys:
        return None
    diffs = [a[k] - b[k] for k in keys]
    return {
        "pairs": len(keys),
        "mean_diff": statistics.fmean(diffs),
        "std_diff": statistics.stdev(diffs) if len(diffs) > 1 else 0.0,
        "wins": sum(d > 0 for d in diffs),
        "ties": sum(d == 0 for d in diffs),
        "losses": sum(d < 0 for d in diffs),
    }


def _fmt(value: Any, digits: int = 2) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def render_markdown(rows: list[dict[str, Any]], table: list[dict[str, Any]]) -> str:
    lines = [
        "# M3 results: planning and self-correction ablations",
        "",
        "_Generated by `M3/summarize_ablations.py`. Re-run it after new runs finish;"
        " edit the interpretation section by hand._",
        "",
    ]
    m3_runs = [r for r in rows if r["method"] != "m1_baseline"]
    if not m3_runs:
        lines += [
            "**Status: no completed M3 ablation runs yet.** Run"
            " `M3/run_ablations.py` (see `M3/EXPERIMENT_RUNBOOK.md`), then re-run"
            " this script.",
            "",
        ]
    lines += [
        "Setup: protocol v1 development systems, ORB v3 oracle, budget 20 queries,"
        " seeds 17/29/43, one episode per seed. mSUN = stable, unique, novel"
        " structures found (primary metric); AUDC = area under the discovery curve.",
        "",
        "## Per-method summary (mean ± std over runs)",
        "",
        "| Method | Runs | mSUN@20 | mSUN fraction | AUDC | AF | EF | Re-plans / run |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for entry in table:
        cells = [
            f"{_fmt(entry[f'{m}_mean'])} ± {_fmt(entry[f'{m}_std'])}"
            if entry[f"{m}_mean"] is not None
            else "n/a"
            for m in METRICS
        ]
        lines.append(
            f"| `{entry['method']}` | {entry['runs']} | "
            + " | ".join(cells)
            + f" | {_fmt(entry['replans_mean'], 1)} |"
        )
    lines += [
        "",
        "## Paired comparisons (same system and seed)",
        "",
        "| Comparison | Measures | Pairs | Δ mSUN (mean ± std) | Better / same / worse | Δ AUDC |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    sentences = []
    for treatment, control, meaning in COMPARISONS:
        result = paired(rows, treatment, control)
        audc = paired(rows, treatment, control, "audc")
        if result is None:
            lines.append(
                f"| `{treatment}` − `{control}` | {meaning} | 0 | n/a | n/a | n/a |"
            )
            continue
        lines.append(
            f"| `{treatment}` − `{control}` | {meaning} | {result['pairs']} | "
            f"{result['mean_diff']:+.2f} ± {result['std_diff']:.2f} | "
            f"{result['wins']} / {result['ties']} / {result['losses']} | "
            f"{_fmt(audc['mean_diff'] if audc else None)} |"
        )
        direction = (
            "more"
            if result["mean_diff"] > 0
            else "fewer"
            if result["mean_diff"] < 0
            else "the same number of"
        )
        sentences.append(
            f"- {meaning.capitalize()}: `{treatment}` found {abs(result['mean_diff']):.2f}"
            f" {direction} stable-unique-novel structures per run than `{control}`"
            f" on average, better in {result['wins']} of {result['pairs']} paired runs"
            f" and worse in {result['losses']}."
        )
    replans = [r for r in rows if r["method"] in ("m3_full", "m3_planning_off")]
    if replans:
        total = sum(r.get("replans") or 0 for r in replans)
        stalls = sum(r.get("replans_no_progress") or 0 for r in replans)
        repeats = sum(r.get("replans_repetition") or 0 for r in replans)
        sentences.append(
            f"- Self-correction re-planned {total} times across {len(replans)} runs with it"
            f" on ({stalls} for no progress in the window, {repeats} for repeated formulas)."
        )
    lines += ["", "## What changed (generated)", ""]
    lines += sentences or ["- Pending: no paired runs yet."]
    lines += [
        "",
        "## Why (interpretation, edit by hand)",
        "",
        "- Planning: compare where `m3_full` and `m3_planning_off` diverge. Without"
        " planning, M1 proposes the full-system composition every query, so"
        " discoveries depend on self-correction alone.",
        "- Self-correction: link re-plan events in each run's `console_attempt_XX.log`"
        " (`M3 re-plan:` lines) to the discoveries that followed them.",
        "- Report neutral or negative differences as found; 18 paired runs are a"
        " small sample, so state the spread, not only the mean.",
        "",
        "Per-run values: `M3/results/m3_ablation_runs.csv`.",
        "",
    ]
    return "\n".join(lines)


def write_outputs(rows: list[dict[str, Any]], out_dir: Path, report: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "m3_ablation_runs.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=RUN_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    table = summarize(rows)
    if table:
        with (out_dir / "m3_ablation_summary.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_markdown(rows, table), encoding="utf-8")


def main() -> None:
    rows = collect()
    write_outputs(rows, M3_DIR / "results", M3_DIR / "report" / "M3_RESULTS.md")
    counts = {m: sum(r["method"] == m for r in rows) for m in METHODS}
    print("Completed runs:", ", ".join(f"{m}={n}" for m, n in counts.items()))
    print(f"Wrote {M3_DIR / 'results'} and {M3_DIR / 'report' / 'M3_RESULTS.md'}")


if __name__ == "__main__":
    main()
