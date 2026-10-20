"""Dev vs held-out generalization table and chart from M2 `evaluate.py` outputs.

Reads the `per_run.csv` written by `M2/evaluate.py` for the development split and
for a held-out split (the public check set, or the course hidden set once the
runner supports it), and writes:

- `generalization_summary.csv`: per method and metric, dev vs held-out mean/SD,
  run counts, completeness and the held-out minus dev gap.
- `per_system.csv`: per method, split and system, seed values and their mean/SD.
- `missing_units.csv`: every expected method/system/seed with no accepted run.
- `generalization.md`: the same tables, ready for the report.
- `generalization.svg`: small multiples (mSUN@B, AUDC, AF and EF vs Random).

Rules:
- A method's headline mean uses M2's aggregation (equal-weight system mean per
  seed, then mean and sample SD across seeds) and is only reported when the
  split is complete for that method. Otherwise it stays blank. The mean over the
  available runs is shown separately and labelled as partial.
- The gap (held-out minus dev) is only computed from two complete headline means.
- Missing runs are listed, never filled in. Nothing is interpolated or imputed.
- For non-baseline methods, dev and held-out runs must come from one repository
  revision (the frozen agent) unless `--allow-mixed-revisions` is given.

Standard library only, so it runs without the MADE environment. Example:

    python M6/generalization.py \
        --dev M2/verification/20261019-chemeleon-recovery/per_run.csv \
        --heldout path/to/check_report/per_run.csv --heldout-split check \
        --output M6/results/generalization-YYYYMMDD
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from html import escape
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
PROTOCOL_DIR = REPO / "M1" / "protocol"
BASELINES = ("random_generator_baseline", "chemeleon_generative_baseline")
DEFAULT_METHODS = ("m1_full", *BASELINES)
DEFAULT_SEEDS = (17, 29, 43)
METRICS = (
    ("mSUN_at_B", "mSUN@B"),
    ("AUDC", "AUDC"),
    ("AF_vs_random", "AF vs Random"),
    ("EF_vs_random", "EF vs Random"),
    ("AF_vs_chemeleon", "AF vs Chemeleon"),
    ("EF_vs_chemeleon", "EF vs Chemeleon"),
)
CHART_METRICS = ("mSUN_at_B", "AUDC", "AF_vs_random", "EF_vs_random")
SHORT_NAMES = {
    "m1_full": "Agent (m1_full)",
    "random_generator_baseline": "Random",
    "chemeleon_generative_baseline": "Chemeleon",
}

Unit = tuple[str, str, int]  # method, system, seed


def number(value: Any) -> float | None:
    """Return a finite float, or None for blank/missing/non-finite cells."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def read_runs(paths: list[Path], split_label: str) -> dict[Unit, dict[str, Any]]:
    """Load one or more per_run.csv files (or report dirs) for one split."""
    runs: dict[Unit, dict[str, Any]] = {}
    for path in paths:
        csv_path = path / "per_run.csv" if path.is_dir() else path
        if not csv_path.is_file():
            raise SystemExit(f"{csv_path} not found")
        with csv_path.open(newline="") as stream:
            for row in csv.DictReader(stream):
                key = (row["method"], row["system"], int(row["seed"]))
                if key in runs:
                    raise SystemExit(
                        f"Duplicate unit {key} in {split_label} input ({csv_path}); "
                        "deduplicate explicitly"
                    )
                row["_source_file"] = str(csv_path)
                runs[key] = row
    return runs


def load_systems(split: str, override: Path | None) -> list[str] | None:
    path = override or PROTOCOL_DIR / f"{split}_systems.json"
    if not path.is_file():
        return None
    return ["-".join(system) for system in json.loads(path.read_text())]


def seed_aggregate(
    runs: dict[Unit, dict[str, Any]],
    method: str,
    systems: list[str],
    seeds: list[int],
    field: str,
) -> tuple[float | None, float | None]:
    """M2's aggregation: equal-weight system mean per seed, then across seeds."""
    seed_means = []
    for seed in seeds:
        values = [number(runs.get((method, s, seed), {}).get(field)) for s in systems]
        if any(v is None for v in values):
            return None, None
        seed_means.append(statistics.mean(values))
    if not seed_means:
        return None, None
    mean = statistics.mean(seed_means)
    sd = statistics.stdev(seed_means) if len(seed_means) > 1 else None
    return mean, sd


def split_stats(
    runs: dict[Unit, dict[str, Any]],
    method: str,
    systems: list[str] | None,
    seeds: list[int],
    field: str,
) -> dict[str, Any]:
    present = [number(row.get(field)) for (m, _, _), row in runs.items() if m == method]
    available = [v for v in present if v is not None]
    if systems is None:
        expected = None
        complete = False
    else:
        expected = len(systems) * len(seeds)
        complete = all((method, s, seed) in runs for s in systems for seed in seeds)
    mean = sd = None
    if complete and systems:
        mean, sd = seed_aggregate(runs, method, systems, seeds, field)
    # AF/EF pairs where the baseline found nothing use MADE's zero-baseline
    # convention (M2 labels them); count them so the report can footnote them.
    zero_baseline = None
    if field.startswith(("AF_vs_", "EF_vs_")):
        column = "comparison_" + field.split("_vs_", 1)[1]
        zero_baseline = sum(
            1
            for (m, _, _), row in runs.items()
            if m == method and row.get(column) == "official_zero_baseline_convention"
        )
    return {
        "zero_baseline_pairs": zero_baseline,
        "runs": len(present),
        "values": len(available),
        "expected": expected,
        "complete": complete and mean is not None,
        "mean": mean,
        "sd": sd,
        "available_mean": statistics.mean(available) if available else None,
    }


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}".rstrip("0").rstrip(".") if digits else str(value)


def check_revisions(
    dev: dict[Unit, dict[str, Any]],
    heldout: dict[Unit, dict[str, Any]],
    methods: list[str],
) -> dict[str, list[str]]:
    revisions: dict[str, set[str]] = defaultdict(set)
    for runs in (dev, heldout):
        for (method, _, _), row in runs.items():
            if method in methods and method not in BASELINES:
                revisions[method].add(row.get("repository_revision") or "unknown")
    return {m: sorted(r) for m, r in revisions.items() if len(r) > 1}


def build(args: argparse.Namespace) -> dict[str, Any]:
    methods = list(args.methods)
    dev = read_runs(args.dev, "dev")
    heldout = read_runs(args.heldout, args.heldout_split) if args.heldout else {}
    for label, runs in (("dev", dev), (args.heldout_split, heldout)):
        budgets = {row.get("B") for row in runs.values()}
        if len(budgets) > 1:
            raise SystemExit(f"Mixed query budgets in {label} input: {budgets}")
        splits = {row.get("split") for row in runs.values()}
        expected_split = "dev" if label == "dev" else args.heldout_split
        if splits - {expected_split}:
            raise SystemExit(f"{label} input contains split(s) {splits}")
    budgets = {row.get("B") for row in [*dev.values(), *heldout.values()]}
    if len(budgets) > 1:
        raise SystemExit(f"Dev and held-out budgets differ: {budgets}")

    mixed = check_revisions(dev, heldout, methods)
    if mixed and not args.allow_mixed_revisions:
        raise SystemExit(
            "Agent runs come from more than one revision (not one frozen agent): "
            f"{mixed}. Rerun at the frozen revision or pass --allow-mixed-revisions."
        )

    splits = {
        "dev": {
            "name": "dev",
            "runs": dev,
            "systems": load_systems("dev", args.dev_systems),
            "seeds": list(args.dev_seeds),
        },
        "heldout": {
            "name": args.heldout_split,
            "runs": heldout,
            "systems": load_systems(args.heldout_split, args.heldout_systems),
            "seeds": list(args.heldout_seeds),
        },
    }
    if splits["heldout"]["systems"] is None and heldout:
        # Hidden list not in the repo yet: show what exists, but nothing is complete.
        splits["heldout"]["systems_note"] = "expected systems unknown"

    summary = []
    for method in methods:
        for field, label in METRICS:
            d = split_stats(
                dev, method, splits["dev"]["systems"], splits["dev"]["seeds"], field
            )
            h = split_stats(
                heldout,
                method,
                splits["heldout"]["systems"],
                splits["heldout"]["seeds"],
                field,
            )
            gap = rel = None
            if d["complete"] and h["complete"]:
                gap = h["mean"] - d["mean"]
                rel = gap / d["mean"] if d["mean"] else None
            status = (
                "complete"
                if gap is not None
                else "incomplete: "
                + f"dev {d['runs']}/{d['expected']}, "
                + f"{args.heldout_split} {h['runs']}/{h['expected'] if h['expected'] is not None else '?'}"
            )
            summary.append(
                {
                    "method": method,
                    "metric": field,
                    "metric_label": label,
                    "dev_runs": d["runs"],
                    "dev_expected": d["expected"],
                    "dev_complete": d["complete"],
                    "dev_mean": d["mean"],
                    "dev_sd": d["sd"],
                    "dev_available_mean_partial": None
                    if d["complete"]
                    else d["available_mean"],
                    "heldout_split": args.heldout_split,
                    "heldout_runs": h["runs"],
                    "heldout_expected": h["expected"],
                    "heldout_complete": h["complete"],
                    "heldout_mean": h["mean"],
                    "heldout_sd": h["sd"],
                    "heldout_available_mean_partial": None
                    if h["complete"]
                    else h["available_mean"],
                    "gap_heldout_minus_dev": gap,
                    "relative_gap": rel,
                    "gap_status": status,
                    "dev_zero_baseline_pairs": d["zero_baseline_pairs"],
                    "heldout_zero_baseline_pairs": h["zero_baseline_pairs"],
                }
            )

    per_system, missing = [], []
    for role, split in splits.items():
        runs, systems, seeds = split["runs"], split["systems"], split["seeds"]
        listed = systems or sorted({s for (_, s, _) in runs})
        for method in methods:
            for system in listed:
                row: dict[str, Any] = {
                    "method": method,
                    "role": role,
                    "split": split["name"],
                    "system": system,
                    "seeds_expected": " ".join(map(str, seeds)),
                    "seeds_available": " ".join(
                        str(seed) for seed in seeds if (method, system, seed) in runs
                    ),
                }
                for field, _ in METRICS:
                    values = [
                        number(runs[(method, system, seed)].get(field))
                        for seed in seeds
                        if (method, system, seed) in runs
                    ]
                    values = [v for v in values if v is not None]
                    row[f"{field}_values"] = " ".join(fmt(v) for v in values)
                    row[f"{field}_mean"] = statistics.mean(values) if values else None
                    row[f"{field}_sd"] = (
                        statistics.stdev(values) if len(values) > 1 else None
                    )
                per_system.append(row)
                if systems is not None:
                    for seed in seeds:
                        if (method, system, seed) not in runs:
                            missing.append(
                                {
                                    "method": method,
                                    "role": role,
                                    "split": split["name"],
                                    "system": system,
                                    "seed": seed,
                                }
                            )
            if systems is None:
                missing.append(
                    {
                        "method": method,
                        "role": role,
                        "split": split["name"],
                        "system": "UNKNOWN (system list not in repo)",
                        "seed": "",
                    }
                )
    return {
        "summary": summary,
        "per_system": per_system,
        "missing": missing,
        "splits": splits,
        "mixed_revisions": mixed,
        "methods": methods,
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row)) or ["empty"]
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if v is None else v for k, v in row.items()})


def cell(
    mean: float | None,
    sd: float | None,
    runs: int,
    expected: int | None,
    partial: float | None,
) -> str:
    total = "?" if expected is None else expected
    if mean is not None:
        return f"{fmt(mean)} ± {fmt(sd)}" if sd is not None else fmt(mean)
    if partial is not None:
        return f"n/a ({runs}/{total} runs; partial mean {fmt(partial)})"
    return f"missing (0/{total} runs)" if runs == 0 else f"n/a ({runs}/{total} runs)"


def show(row: dict[str, Any], field: str) -> str:
    if row[f"{field}_mean"] is None:
        return "missing"
    text = fmt(row[f"{field}_mean"])
    if row[f"{field}_sd"] is not None:
        text += f" ± {fmt(row[f'{field}_sd'])}"
    return f"{text} [{row[f'{field}_values']}]"


def write_markdown(path: Path, result: dict[str, Any], heldout_split: str) -> None:
    held = (
        "public check set (not the course hidden test)"
        if heldout_split == "check"
        else heldout_split
    )
    lines = [
        "# Generalization: development vs held-out",
        "",
        f"Held-out split: **{held}**. Headline values use M2's aggregation (equal-weight "
        "system mean per seed, then mean ± sample SD across seeds) and appear only when "
        "the split is complete for that method. `n/a` means incomplete; partial means "
        "are over available runs only and are not comparable. Gap = held-out − dev.",
        "",
        "| Method | Metric | Dev | Held-out | Gap | Relative gap |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["summary"]:
        dev = cell(
            row["dev_mean"],
            row["dev_sd"],
            row["dev_runs"],
            row["dev_expected"],
            row["dev_available_mean_partial"],
        )
        hel = cell(
            row["heldout_mean"],
            row["heldout_sd"],
            row["heldout_runs"],
            row["heldout_expected"],
            row["heldout_available_mean_partial"],
        )
        gap = fmt(row["gap_heldout_minus_dev"]) or "n/a"
        rel = (
            f"{row['relative_gap'] * 100:.1f} %"
            if row["relative_gap"] is not None
            else "n/a"
        )
        name = SHORT_NAMES.get(row["method"], row["method"])
        lines.append(
            f"| {name} | {row['metric_label']} | {dev} | {hel} | {gap} | {rel} |"
        )
    lines += [
        "",
        "## Per system (mSUN@B and AUDC; seed values in brackets)",
        "",
        "| Method | Split | System | Seeds present | mSUN@B | AUDC |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in result["per_system"]:
        seeds = row["seeds_available"] or "none"
        lines.append(
            f"| {SHORT_NAMES.get(row['method'], row['method'])} | {row['split']} | {row['system']} "
            f"| {seeds} of {row['seeds_expected']} | {show(row, 'mSUN_at_B')} | {show(row, 'AUDC')} |"
        )
    zero = [
        f"{SHORT_NAMES.get(r['method'], r['method'])} {r['metric_label']} "
        f"(dev {r['dev_zero_baseline_pairs']}, held-out {r['heldout_zero_baseline_pairs']})"
        for r in result["summary"]
        if r["dev_zero_baseline_pairs"] or r["heldout_zero_baseline_pairs"]
    ]
    if zero:
        lines += [
            "",
            "Zero-baseline pairs (the baseline found nothing; MADE's official convention "
            "sets the factor, see `comparison_*` in M2's per_run.csv): "
            + "; ".join(zero)
            + ".",
        ]
    lines += ["", f"Missing units: {len(result['missing'])} (see `missing_units.csv`)."]
    if result["mixed_revisions"]:
        lines.append(
            f"WARNING: agent runs from several revisions: {result['mixed_revisions']}"
        )
    path.write_text("\n".join(lines) + "\n")


# Reference categorical slots 1-2 (dataviz skill palette), light surface.
DEV_COLOR, HELD_COLOR = "#2a78d6", "#eb6834"


def write_svg(path: Path, result: dict[str, Any], heldout_split: str) -> None:
    """Small multiples in a 2x2 grid, one panel and one y-scale per metric."""
    methods = result["methods"]
    by_key = {(r["method"], r["metric"]): r for r in result["summary"]}
    per_sys = defaultdict(list)
    for row in result["per_system"]:
        per_sys[(row["method"], row["role"])].append(row)
    held_label = (
        "Public check set" if heldout_split == "check" else heldout_split.capitalize()
    )
    pw, ph, left, gap_x, panel_h = 380, 170, 48, 56, 250
    top = 92
    width = left + 2 * pw + gap_x + 24
    height = top + 2 * panel_h + 8
    ink, ink2, grid, surface = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="Helvetica, Arial, sans-serif">',
        f'<rect width="{width}" height="{height}" fill="{surface}"/>',
        f'<text x="16" y="26" font-size="16" font-weight="600" fill="{ink}">'
        f"Development vs held-out ({escape(held_label)})</text>",
        f'<text x="16" y="45" font-size="11" fill="{ink2}">Bar = mean of available '
        "runs (faded = incomplete). Dots = per-system means. Dashed = no runs. "
        "Counts = runs present / expected.</text>",
    ]
    for i, (label, color) in enumerate((("Dev", DEV_COLOR), (held_label, HELD_COLOR))):
        lx = 16 + i * 80
        out.append(
            f'<rect x="{lx}" y="59" width="12" height="12" rx="2" fill="{color}"/>'
        )
        out.append(
            f'<text x="{lx + 18}" y="69" font-size="12" fill="{ink}">{escape(label)}</text>'
        )
    for p, metric in enumerate(CHART_METRICS):
        x0 = left + (p % 2) * (pw + gap_x)
        y0 = top + (p // 2) * panel_h + 20
        label = dict(METRICS)[metric]
        values = []
        for method in methods:
            for role in ("dev", "heldout"):
                row = by_key[(method, metric)]
                values.append(
                    row[f"{role}_mean"]
                    if row[f"{role}_complete"]
                    else row[f"{role}_available_mean_partial"]
                )
                values += [r[f"{metric}_mean"] for r in per_sys[(method, role)]]
        finite = [v for v in values if v is not None]
        ymax = max(finite) * 1.1 if finite and max(finite) > 0 else 1.0
        out.append(
            f'<text x="{x0}" y="{y0 - 8}" font-size="13" font-weight="600" '
            f'fill="{ink}">{escape(label)}</text>'
        )
        for t in range(5):
            y = y0 + ph - ph * t / 4
            out.append(
                f'<line x1="{x0}" x2="{x0 + pw}" y1="{y:.1f}" y2="{y:.1f}" '
                f'stroke="{grid}" stroke-width="1"/>'
            )
            out.append(
                f'<text x="{x0 - 6}" y="{y + 3:.1f}" font-size="10" '
                f'text-anchor="end" fill="{ink2}">{fmt(ymax * t / 4, 1)}</text>'
            )
        group = pw / max(len(methods), 1)
        bw = min(34, group / 3)
        for m, method in enumerate(methods):
            cx = x0 + group * m + group / 2
            row = by_key[(method, metric)]
            name = SHORT_NAMES.get(method, method)
            for r, (role, color) in enumerate(
                (("dev", DEV_COLOR), ("heldout", HELD_COLOR))
            ):
                bx = cx - bw - 1 + r * (bw + 2)
                complete = row[f"{role}_complete"]
                value = (
                    row[f"{role}_mean"]
                    if complete
                    else row[f"{role}_available_mean_partial"]
                )
                expected = row[f"{role}_expected"]
                count = f"{row[f'{role}_runs']}/{'?' if expected is None else expected}"
                out.append(
                    f'<text x="{bx + bw / 2:.1f}" y="{y0 + ph + 13}" font-size="9" '
                    f'text-anchor="middle" fill="{ink2}">{count}</text>'
                )
                if value is None:
                    out.append(
                        f'<rect x="{bx + 1:.1f}" y="{y0 + ph - 10}" width="{bw - 2:.1f}" '
                        f'height="10" fill="none" stroke="{color}" stroke-width="1.5" '
                        f'stroke-dasharray="3 2"><title>{escape(name)} {role}: no runs '
                        f"({count})</title></rect>"
                    )
                    continue
                h = max(ph * value / ymax, 4)
                tip = f"{name} {role}: {fmt(value)} ({count} runs"
                tip += ")" if complete else ", incomplete)"
                out.append(
                    f'<path d="M{bx:.1f},{y0 + ph} v{-(h - 4):.1f} q0,-4 4,-4 '
                    f'h{bw - 8:.1f} q4,0 4,4 v{h - 4:.1f} z" fill="{color}" '
                    f'fill-opacity="{1 if complete else 0.4}"><title>{escape(tip)}'
                    "</title></path>"
                )
                for srow in per_sys[(method, role)]:
                    sv = srow[f"{metric}_mean"]
                    if sv is not None:
                        sy = y0 + ph - ph * sv / ymax
                        out.append(
                            f'<circle cx="{bx + bw / 2:.1f}" cy="{sy:.1f}" r="3" '
                            f'fill="{ink}" stroke="{surface}" stroke-width="1.5">'
                            f"<title>{escape(srow['system'])}: {fmt(sv)}</title></circle>"
                        )
            out.append(
                f'<text x="{cx:.1f}" y="{y0 + ph + 30}" font-size="11" '
                f'text-anchor="middle" fill="{ink}">'
                f"{escape(name.replace(' (m1_full)', ''))}</text>"
            )
        out.append(
            f'<line x1="{x0}" x2="{x0 + pw}" y1="{y0 + ph}" y2="{y0 + ph}" '
            f'stroke="{ink2}" stroke-width="1"/>'
        )
    out.append("</svg>")
    path.write_text("\n".join(out) + "\n")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--dev",
        type=Path,
        nargs="+",
        required=True,
        help="Dev per_run.csv file(s) or report dir(s)",
    )
    parser.add_argument(
        "--heldout",
        type=Path,
        nargs="*",
        default=[],
        help="Held-out per_run.csv file(s); omit if none yet",
    )
    parser.add_argument("--heldout-split", choices=("check", "hidden"), default="check")
    parser.add_argument(
        "--output", type=Path, required=True, help="New or empty output directory"
    )
    parser.add_argument("--methods", nargs="+", default=list(DEFAULT_METHODS))
    parser.add_argument("--dev-seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument(
        "--heldout-seeds",
        type=int,
        nargs="+",
        default=list(DEFAULT_SEEDS),
        help="Use 17 alone for the 1-seed fallback",
    )
    parser.add_argument(
        "--dev-systems", type=Path, help="Override dev system list JSON"
    )
    parser.add_argument(
        "--heldout-systems", type=Path, help="Override held-out system list JSON"
    )
    parser.add_argument("--allow-mixed-revisions", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.output.exists() and any(args.output.iterdir()):
        raise SystemExit(
            f"{args.output} already contains files; choose a new directory"
        )
    result = build(args)
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "generalization_summary.csv", result["summary"])
    write_csv(args.output / "per_system.csv", result["per_system"])
    write_csv(args.output / "missing_units.csv", result["missing"])
    write_markdown(args.output / "generalization.md", result, args.heldout_split)
    write_svg(args.output / "generalization.svg", result, args.heldout_split)
    complete = sum(
        1 for r in result["summary"] if r["gap_heldout_minus_dev"] is not None
    )
    print(
        json.dumps(
            {
                "output": str(args.output),
                "dev_runs": len(result["splits"]["dev"]["runs"]),
                "heldout_runs": len(result["splits"]["heldout"]["runs"]),
                "missing_units": len(result["missing"]),
                "complete_gaps": complete,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
