"""Make a real, small Materials Project request without revealing credentials."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    from mp_api.client import MPRester

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    key = os.environ.get("MATERIALS_PROJECT_API_KEY", "").strip()
    if len(key) != 32:
        raise SystemExit(
            "A valid-format Materials Project repository secret is required"
        )
    repo = Path(__file__).resolve().parents[1]
    system = json.loads((repo / "M1/protocol/dev_systems.json").read_text())[0]
    report = {
        "kind": "actual_materials_project_access_check",
        "benchmark_score": False,
        "system": system,
        "endpoint": "materials/summary",
        "max_documents": 1,
        "status": "failed",
    }
    try:
        with MPRester(api_key=key) as client:
            documents = client.materials.summary.search(
                chemsys="-".join(system),
                num_chunks=1,
                chunk_size=1,
                fields=["material_id"],
            )
            report.update(
                status="accepted",
                documents_returned=len(documents),
                material_ids=[str(item.material_id) for item in documents],
                database_version=client.get_database_version(),
            )
    except Exception as error:
        report["error"] = f"{type(error).__name__}: {error}".replace(key, "[REDACTED]")
    report["checked_at_utc"] = datetime.now(UTC).isoformat()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if report["status"] != "accepted":
        raise SystemExit("The actual Materials Project request failed; see the report")


if __name__ == "__main__":
    main()
