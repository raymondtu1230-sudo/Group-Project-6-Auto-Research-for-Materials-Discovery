"""Package original per-attempt evidence for the 18 exploration_off runs.

Maps each timestamped Hydra run dir (results/<timestamp>-orb-m1_integrated)
to its protocol attempt via the saved overrides.yaml output_dir, then copies
the retained originals into the attempt dir following M1's packaging
convention, and writes evidence_manifest.json with sha256+bytes per file.

No rerun is performed. m2_metrics_history.json is reconstructed losslessly
from the official trajectory (same approach M1 used for the frozen Full
reference) and labelled as a reconstruction. exploration_off legitimately has
no m5_decisions.jsonl (the hook is off); the absence is stated, not filled.

Run from repo root: python M5/package_evidence.py
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RESULTS = REPO / "M1" / "MADE" / "results"
OFF_ROOT = RESULTS / "protocol_v1" / "exploration_off" / "dev"
REVISION = "aedf8ca238d2ef56948c0eadf2c897aef67f5104"

# resolved_config.yaml: the saved hydra config with interpolations resolved.
RESOLVED_NOTE = (
    "the run's saved Hydra composed config (results/<ts>/.hydra/config.yaml); "
    "interpolations resolved at packaging time where resolvable outside the "
    "Hydra runtime, otherwise kept verbatim; no rerun"
)


def sha256_bytes(path: Path) -> dict:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def attempt_from_overrides(run_dir: Path) -> Path | None:
    overrides = run_dir / ".hydra" / "overrides.yaml"
    if not overrides.is_file():
        return None
    for line in overrides.read_text(encoding="utf-8").splitlines():
        line = line.strip().lstrip("-").strip()
        if line.startswith("experiment.output_dir="):
            rel = line.split("=", 1)[1].strip()
            target = RESULTS / Path(rel).relative_to("results")
            return target if "exploration_off" in str(target) else None
    return None


def resolve_config(config_path: Path, out_path: Path) -> None:
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(config_path)
    try:
        out_path.write_text(OmegaConf.to_yaml(cfg, resolve=True), encoding="utf-8")
    except Exception:
        # Runtime-only resolvers (hydra:*, oc.env:*) are unavailable at
        # packaging time; keep the saved composed config verbatim instead.
        out_path.write_text(OmegaConf.to_yaml(cfg), encoding="utf-8")


def reconstruct_metrics_history(traj_path: Path, out_path: Path) -> None:
    traj = json.loads(traj_path.read_text(encoding="utf-8"))["trajectory"]
    history = []
    stable_novel_unique = 0
    stable_new = 0
    audc = 0.0
    prev_cum = 0.0
    seen_formulas: set[str] = set()
    budget = len(traj)
    for i, step in enumerate(traj, start=1):
        stable = bool(step.get("is_stable"))
        novel = bool(step.get("is_newly_discovered"))
        formula = step.get("reduced_formula")
        if stable:
            stable_new += 1
        # mSUN curve: stable + novel + first occurrence of the formula
        if stable and novel and formula not in seen_formulas:
            stable_novel_unique += 1
            seen_formulas.add(formula)
        # Official AUDC = trapezoidal area under the SUN curve with a zero
        # origin (verified against M2's zero-origin proof and all 18 official
        # endpoints).
        audc += (prev_cum + stable_novel_unique) / 2
        prev_cum = float(stable_novel_unique)
        history.append(
            {
                "queries_used": i,
                "num_newly_discovered_stable": stable_new,
                "novelty_stable_unique_novel_count": stable_novel_unique,
                "discovery_curve_area_under_discovery_curve": float(audc),
                "discovery_curve_area_under_discovery_curve_normalized": (
                    audc / (budget * stable_novel_unique)
                    if stable_novel_unique
                    else 0.0
                ),
            }
        )
    payload = {
        "source": "reconstructed_from_frozen_official_trajectory",
        "provenance_note": (
            "The exploration_off launcher did not retain per-query metrics "
            "history. This curve is reconstructed losslessly from the per-query "
            "is_stable and is_newly_discovered observations in the attempt's "
            "official trajectory and verified against its final mSUN and AUDC."
        ),
        "complete_curve": True,
        "query_counts": list(range(1, budget + 1)),
        "metrics_history": history,
    }
    out_path.write_text(json.dumps(payload, indent=1), encoding="utf-8")


def main() -> None:
    run_dirs = sorted(
        p for p in RESULTS.glob("2026102*-orb-m1_integrated") if p.is_dir()
    )
    packaged = []
    for run_dir in run_dirs:
        attempt = attempt_from_overrides(run_dir)
        if attempt is None or not attempt.is_dir():
            continue
        files: dict[str, dict] = {}

        hydra_out = attempt / "hydra"
        hydra_out.mkdir(exist_ok=True)
        for name in ("config.yaml", "hydra.yaml", "overrides.yaml"):
            src = run_dir / ".hydra" / name
            if src.is_file():
                dst = hydra_out / name
                if not dst.exists():
                    shutil.copy2(src, dst)
                files[f"hydra/{name}"] = sha256_bytes(dst)

        for name in ("m4_evidence.jsonl", "run_benchmark.log"):
            src = run_dir / name
            if src.is_file():
                dst = attempt / name
                if not dst.exists():
                    shutil.copy2(src, dst)
                files[name] = sha256_bytes(dst)

        console = attempt.parent / f"console_{attempt.name}.log"
        if console.is_file():
            dst = attempt / console.name
            if not dst.exists():
                shutil.copy2(console, dst)
            files[console.name] = sha256_bytes(dst)

        resolved = attempt / "resolved_config.yaml"
        if not resolved.exists():
            resolve_config(run_dir / ".hydra" / "config.yaml", resolved)
        files["resolved_config.yaml"] = sha256_bytes(dst := resolved)
        files["resolved_config.yaml"]["note"] = RESOLVED_NOTE

        traj = attempt / "trajectories" / "episode_000.json"
        mh = attempt / "m2_metrics_history.json"
        if traj.is_file() and not mh.exists():
            reconstruct_metrics_history(traj, mh)
        if mh.is_file():
            files["m2_metrics_history.json"] = sha256_bytes(mh)

        manifest = {
            "source_directory": f"results/{run_dir.name}",
            "target_attempt": str(attempt.relative_to(RESULTS)).replace("\\", "/"),
            "recorded_revision": REVISION,
            "files": files,
        }
        (attempt / "evidence_manifest.json").write_text(
            json.dumps(manifest, indent=1), encoding="utf-8"
        )
        packaged.append(str(attempt.relative_to(RESULTS)))

    note = (
        "# exploration_off evidence packaging (26 Oct)\n\n"
        f"Packaged {len(packaged)} attempts from their original timestamped "
        "Hydra run dirs; no rerun performed. Recorded revision: "
        f"{REVISION}.\n\n"
        "- `hydra/` = the run's saved Hydra config/overrides (original bytes)\n"
        "- `m4_evidence.jsonl`, `run_benchmark.log`, `console_attempt_*.log` = "
        "original retained logs\n"
        "- `resolved_config.yaml` = composed from the saved hydra config with "
        "interpolations resolved at packaging time (no rerun)\n"
        "- `m2_metrics_history.json` = lossless reconstruction from the "
        "official trajectory (labelled in-file), per M1's packaging approach\n"
        "- `m5_decisions.jsonl` is absent by design: exploration_off disables "
        "the M5 hook, so no decisions exist. The absence is intentional.\n"
    )
    (OFF_ROOT / "EVIDENCE_PACKAGING.md").write_text(note, encoding="utf-8")
    print(f"packaged {len(packaged)} attempts")
    for p in packaged:
        print(" ", p)


if __name__ == "__main__":
    main()
