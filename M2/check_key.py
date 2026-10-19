"""Validate credential presence and formatting without revealing its value."""

from __future__ import annotations

import os


def main() -> None:
    key = os.environ.get("MATERIALS_PROJECT_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "The TUWEIKANG_MATERIALS_PROJECT_API_KEY repository secret is missing."
        )
    if len(key) != 32:
        raise SystemExit(
            "Materials Project expects a 32-character API key. "
            "Copy the key value from https://materialsproject.org/api, "
            "without quotes or an environment variable name."
        )
    print("Credential format accepted; the real API request will verify access.")


if __name__ == "__main__":
    main()
