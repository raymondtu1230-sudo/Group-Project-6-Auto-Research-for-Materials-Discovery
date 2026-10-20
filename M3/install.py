"""Install or check M3's files in the M1 MADE checkout.

``M3/integration/M1/...`` holds everything M3 adds to or changes in M1, at the
paths M1 uses. The ``main`` branch carries only ``M3/``; M1 stays unchanged
until this installer is run.

- New M3 files (module, configs, tests) are copied in.
- M1-owned files that M3 edits (``m1_integrated.yaml``, ``run_experiment.py``,
  M1's protocol test and protocol doc) are replaced only if they are still
  the version M3 was prepared against (M1 revision ``fcaaccc``). Once M1 has
  integrated M3, M1 owns these files and may merge other members' settings
  into them. A file counts as "merged" when it still contains every M3 edit
  (``M3_MARKERS``), and the installer leaves it alone. Any other change stops
  the installer, which names the file so the edit can be merged by hand.

From the repository root or anywhere::

    python M3/install.py            # check whether M3 is in M1
    python M3/install.py --install  # install
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
from pathlib import Path

M3_DIR = Path(__file__).resolve().parent
REPO = M3_DIR.parent
SOURCE = M3_DIR / "integration"
NEW_FILES = (
    "M1/MADE/src/made/agents/m3_planning.py",
    "M1/MADE/configs/agent/planner/m3_research.yaml",
    "M1/MADE/configs/agent/self_correction_policy/m3_stuck_replan.yaml",
    "M1/MADE/tests/test_m3_planning.py",
)
# M1-owned files M3 edits -> sha256 of the M1 version the edit was made against
# (line endings normalised).
EDITED_FILES = {
    "M1/MADE/configs/agent/m1_integrated.yaml": "7793945f1f057238e83ee110feb196741c8f3e7045d6e5787ba8cbe9fca3d6ae",
    "M1/run_experiment.py": "139f797b0d46a0727932a3ea4fe94d7280649fdfa93d577e9b421b5115ab19ba",
    "M1/tests/test_protocol.py": "3868cd87568bc025098d1d8bbcc3712b8ba7dea3ff3ff3583a8d8ea6cab1f6b6",
    "M1/EXPERIMENT_PROTOCOL.md": "ebfa91c190379aba50aacc683b3510eb427bfdd31bc8e72273b8d2c8386ee026",
}
FILES = (*NEW_FILES, *EDITED_FILES)
# Lines that carry M3's edit in each M1-owned file. M1 may add its own settings
# around them (e.g. M4's memory manager, M5's exploration policy).
M3_MARKERS = {
    "M1/MADE/configs/agent/m1_integrated.yaml": (
        "- planner: diversity",
        "- self_correction_policy: m3_stuck_replan",
    ),
    "M1/run_experiment.py": (
        'M3_METHODS = ("m3_full", "m3_planning_off", "m3_self_correction_off")',
        'overrides.append("agent/planner=m3_research")',
        "overrides.extend(m1_agent_overrides(args.method))",
    ),
    "M1/tests/test_protocol.py": (
        "def test_m3_methods_run_against_m1_baseline_without_other_plugins",
        "def test_plugin_complete_methods_keep_all_switches_and_use_m3_planner",
    ),
    "M1/EXPERIMENT_PROTOCOL.md": (
        "| M3 full (`m3_full`) |",
        "| M3 planning ablation (`m3_planning_off`) |",
        "| M3 self-correction ablation (`m3_self_correction_off`) |",
    ),
}


def _text_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _same(a: Path, b: Path) -> bool:
    # Compare text with normalised line endings (Windows checkouts may use CRLF).
    return _text_hash(a) is not None and _text_hash(a) == _text_hash(b)


def has_m3_edit(path: Path, relative: str) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return all(marker in text for marker in M3_MARKERS[relative])


def status(relative: str) -> str:
    """ok | merged | not installed | changed by M1 | missing."""
    target = REPO / relative
    if _same(SOURCE / relative, target):
        return "ok"
    if relative in EDITED_FILES:
        if has_m3_edit(target, relative):
            return "merged"
        if _text_hash(target) == EDITED_FILES[relative]:
            return "not installed"
        return "changed by M1" if target.is_file() else "missing"
    return "not installed"


def mismatches() -> list[str]:
    """Files where M3 is not (fully) present in M1."""
    return [f for f in FILES if status(f) not in ("ok", "merged")]


def conflicts() -> list[str]:
    """M1-owned files changed by M1 without M3's edit; merge by hand."""
    return [f for f in EDITED_FILES if status(f) in ("changed by M1", "missing")]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    if args.install:
        blocked = conflicts()
        if blocked:
            sys.exit(
                "M1 changed these files after M3 was prepared; merge the M3 edit"
                " from M3/integration by hand, then re-run:\n  " + "\n  ".join(blocked)
            )
        for relative in mismatches():
            target = REPO / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / relative, target)
            print(f"installed {relative}")
        print("M3 is installed in M1")
        return
    for relative in FILES:
        print(f"{status(relative):<14} {relative}")
    if conflicts():
        sys.exit("M1 files changed without M3's edit; merge from M3/integration")
    if mismatches():
        sys.exit("M3 is not installed in M1; run: python M3/install.py --install")
    print("M3 is installed in M1 ('merged' = M1's file with M3's edit kept)")


if __name__ == "__main__":
    main()
