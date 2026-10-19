"""Cost and usage accounting for reproducible M1 runs.

The benchmark has three separable accounting domains: oracle queries, data/API
requests, and optional LLM usage.  This module records all three without
guessing prices.  LLM integrations can provide usage through environment
variables or a JSON file; missing usage is reported as ``not_reported``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _load_llm_usage() -> dict[str, Any]:
    path = os.getenv("M1_LLM_USAGE_FILE")
    if path:
        usage_path = Path(path).expanduser()
        if usage_path.exists():
            payload = json.loads(usage_path.read_text())
            if not isinstance(payload, dict):
                raise ValueError("M1_LLM_USAGE_FILE must contain a JSON object")
            return payload
    return {
        "calls": os.getenv("M1_LLM_CALLS"),
        "input_tokens": os.getenv("M1_LLM_INPUT_TOKENS"),
        "output_tokens": os.getenv("M1_LLM_OUTPUT_TOKENS"),
        "cost_usd": os.getenv("M1_LLM_COST_USD"),
        "provider": os.getenv("M1_LLM_PROVIDER"),
        "model": os.getenv("M1_LLM_MODEL"),
    }


def build_cost_record(
    *,
    output_dir: Path,
    method: str,
    status: str,
    query_budget: int,
    wall_time_seconds: float | None,
) -> dict[str, Any]:
    """Build a serializable cost record for one protocol invocation."""
    trajectory_files = sorted((output_dir / "trajectories").glob("episode_*.json"))
    oracle_queries = 0
    for path in trajectory_files:
        payload = json.loads(path.read_text())
        if isinstance(payload, dict):
            steps = payload.get("steps", payload.get("trajectory", []))
            if isinstance(steps, list):
                oracle_queries += len(steps)

    usage = _load_llm_usage()
    input_tokens = _int(usage.get("input_tokens"), -1)
    output_tokens = _int(usage.get("output_tokens"), -1)
    llm_calls = _int(usage.get("calls"), -1)
    llm_cost = usage.get("cost_usd")
    llm_cost_value = _number(llm_cost) if llm_cost is not None else None
    llm_reported = any(value >= 0 for value in (input_tokens, output_tokens, llm_calls)) or llm_cost is not None

    # MP dataset retrieval is one logical request from M1's dataset adapter.
    mp_loaded = status == "completed" or bool(trajectory_files)
    return {
        "accounting_version": "m1-cost-v1",
        "method": method,
        "status": status,
        "oracle": {
            "name": "ORB",
            "queries": oracle_queries,
            "query_budget": query_budget,
            "cost_usd": 0.0,
            "cost_status": "zero_priced_model_inference",
        },
        "materials_project": {
            "logical_dataset_requests": 1 if mp_loaded else 0,
            "cost_usd": 0.0 if mp_loaded else None,
            "cost_status": "public_api_no_unit_price_recorded" if mp_loaded else "not_reached",
        },
        "llm": {
            "provider": usage.get("provider"),
            "model": usage.get("model"),
            "calls": max(llm_calls, 0) if llm_calls >= 0 else None,
            "input_tokens": max(input_tokens, 0) if input_tokens >= 0 else None,
            "output_tokens": max(output_tokens, 0) if output_tokens >= 0 else None,
            "cost_usd": llm_cost_value,
            "cost_status": "reported_by_integration" if llm_reported else "not_reported",
        },
        "total_known_cost_usd": llm_cost_value if llm_cost_value is not None else 0.0,
        "total_cost_status": "complete" if llm_reported or method.endswith("baseline") else "partial",
        "wall_time_seconds": wall_time_seconds,
    }
