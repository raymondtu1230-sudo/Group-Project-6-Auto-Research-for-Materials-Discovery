"""Install or check M3's files in the M1 MADE checkout.

``M3/integration/M1/...`` holds everything M3 adds to or changes in M1, at the
paths M1 uses. The ``main`` branch carries only ``M3/``; M1 stays unchanged
until this installer is run.

- New M3 files (module, configs, tests) are copied in.
- M1-owned files that M3 edits (``m1_integrated.yaml``, ``run_experiment.py``,
  M1's protocol test and protocol doc) are replaced only if they are still
  the version M3 was prepared against (M1 revision ``fcaaccc``). If M1 has
  changed one since, the installer stops and names it so the edit can be
  merged by hand.

From the repository root or anywhere::

    python M3/install.py            # check whether M1 matches M3/integration
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


def _text_hash(path: Path) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8").splitlines()
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def _same(a: Path, b: Path) -> bool:
    # Compare text with normalised line endings (Windows checkouts may use CRLF).
    return _text_hash(a) is not None and _text_hash(a) == _text_hash(b)


def mismatches() -> list[str]:
    return [f for f in FILES if not _same(SOURCE / f, REPO / f)]


def conflicts() -> list[str]:
    """M1-owned files changed by M1 since M3's edit was prepared."""
    return [
        f
        for f, base in EDITED_FILES.items()
        if not _same(SOURCE / f, REPO / f) and _text_hash(REPO / f) != base
    ]


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
        print("M1 now matches M3/integration")
        return
    bad = mismatches()
    for relative in FILES:
        print(f"{'differs' if relative in bad else 'ok     '}  {relative}")
    if bad:
        sys.exit("M3 is not installed in M1; run: python M3/install.py --install")


if __name__ == "__main__":
    main()
