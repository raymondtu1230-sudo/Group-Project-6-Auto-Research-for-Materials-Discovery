"""Preview a missing-only request; --submit explicitly dispatches via a branch commit."""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import uuid

REPOSITORY = "raymondtu1230-sudo/Group-Project-6-Auto-Research-for-Materials-Discovery"
BRANCH = "m2/tool-routing-evaluation"
PATH = "M2/requests/chemeleon-direct.json"


def gh(*args: str, body: dict | None = None) -> str:
    return subprocess.check_output(
        ["gh", *args], input=json.dumps(body) if body else None, text=True
    ).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-sha",
        required=True,
        help="Exact main commit whose executable M2 source passed preflight",
    )
    parser.add_argument("--parallel", type=int, choices=range(1, 18), default=4)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument(
        "--retry-of",
        default="{}",
        help="JSON unit-to-previous-attempt map; terminal failure/timeout only",
    )
    parser.add_argument(
        "--units",
        default="all_missing",
        help="all_missing or JSON list of system/seed objects",
    )
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_sha):
        parser.error("source-sha must be an exact 40-character commit SHA")
    request = {
        "mode": "formal_direct",
        "source_sha": args.source_sha,
        "max_parallel": args.parallel,
        "units": args.units if args.units == "all_missing" else json.loads(args.units),
        "retry_of": json.loads(args.retry_of),
        "request_id": str(uuid.uuid4()),
        "acknowledgement": "RUN_ONLY_MISSING_DEV_CHEMELEON_B20_NO_RESUME",
    }
    print(json.dumps(request, indent=2))
    if not args.submit:
        print(
            "PREVIEW ONLY. Nothing submitted. Add --submit only when formal runs are authorized."
        )
        return
    endpoint = f"repos/{REPOSITORY}/contents/{PATH}"
    old_sha = None
    try:
        old_sha = json.loads(gh("api", endpoint + "?ref=" + BRANCH))["sha"]
    except subprocess.CalledProcessError:
        # Confirm the branch and authentication exist; a missing request is expected on first use.
        gh("api", f"repos/{REPOSITORY}/branches/{BRANCH}")
    body = {
        "branch": BRANCH,
        "message": "Request missing-only M2 direct Chemeleon " + request["request_id"],
        "content": base64.b64encode(
            (json.dumps(request, indent=2) + "\n").encode()
        ).decode(),
    }
    if old_sha:
        body["sha"] = old_sha
    response = json.loads(
        gh("api", "--method", "PUT", endpoint, "--input", "-", body=body)
    )
    print("Submitted branch request commit: " + response["commit"]["sha"])
    print(f"https://github.com/{REPOSITORY}/actions")


if __name__ == "__main__":
    main()
