"""Install the M5 exploration component into M1's MADE tree.

Copies the module, config block and tests from M5/ into the documented M1
slots. Run from the repository root:

    python M5/install.py

Idempotent: existing identical files are left untouched.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MADE = ROOT / "M1" / "MADE"

COPIES = [
    (
        ROOT / "M5" / "src" / "made" / "agents" / "m5_exploration.py",
        MADE / "src" / "made" / "agents" / "m5_exploration.py",
    ),
    (
        ROOT / "M5" / "tests" / "test_m5_exploration.py",
        MADE / "tests" / "test_m5_exploration.py",
    ),
    (
        ROOT / "M5" / "configs" / "m5_exploration_block.yaml",
        MADE / "configs" / "agent" / "m5_exploration_block.yaml",
    ),
]


def main() -> None:
    for source, target in COPIES:
        if not source.exists():
            raise FileNotFoundError(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.read_bytes() == source.read_bytes():
            print(f"unchanged: {target.relative_to(ROOT)}")
            continue
        shutil.copy2(source, target)
        print(f"installed: {target.relative_to(ROOT)}")
    print(
        "\nNext: wire the config block into configs/agent/m1_integrated.yaml "
        "(see M5/README.md), then run:\n"
        "  cd M1/MADE\n"
        "  uv run pytest -q tests/test_m1_integrated.py tests/test_m5_exploration.py\n"
        "  uv run ruff check src/made/agents/m5_exploration.py tests/test_m5_exploration.py"
    )


if __name__ == "__main__":
    main()
