#!/usr/bin/env bash
# Run both required baselines over a held-out split (default: check), serially,
# one system x seed at a time, through M2's capture wrapper around the unchanged
# M1 protocol driver:
#
#   M2/run_baselines.py  ->  M1/run_experiment.py  ->  official scripts/run_benchmark.py
#
# The wrapper is needed because M2/evaluate.py only scores runs that carry the
# official per-query history (m2_metrics_history.json), which only it records.
#
# Safety:
#   - Dry run by default. Nothing is launched without --execute.
#   - A unit with a completed attempt is skipped.
#   - Otherwise the next free attempt number is used. Existing attempts,
#     including failed ones, are never overwritten or deleted.
#   - Ablations and agent variants are refused: check/hidden take baselines only
#     (M6/PROTOCOL_ADOPTION.md).
#
# Usage (from anywhere):
#   M6/run_check_baselines.sh                         # dry run, both baselines, check split
#   M6/run_check_baselines.sh --execute               # run it (Chemeleon ~4.4 h per unit!)
#   M6/run_check_baselines.sh --methods random_generator_baseline --execute
#   M6/run_check_baselines.sh --split hidden --seeds 17 --execute   # once M1 adds "hidden"
#
# Env:
#   M6_RESULTS_ROOT  override the results root (tests only; default M1/MADE/results/protocol_v1)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
MADE="$REPO/M1/MADE"
PROTOCOL_DIR="$REPO/M1/protocol"
RESULTS_ROOT="${M6_RESULTS_ROOT:-$MADE/results/protocol_v1}"
BASELINES="random_generator_baseline chemeleon_generative_baseline"

SPLIT="check"
METHODS="$BASELINES"
SEEDS=""
ONLY_SYSTEMS=""
EXECUTE=0

usage() {
  sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --split) SPLIT="$2"; shift 2 ;;
    --methods) METHODS="$2"; shift 2 ;;
    --seeds) SEEDS="$2"; shift 2 ;;
    --systems) ONLY_SYSTEMS="$2"; shift 2 ;;
    --execute) EXECUTE=1; shift ;;
    -h|--help) usage 0 ;;
    *) echo "Unknown argument: $1" >&2; usage 2 ;;
  esac
done

if [ "$SPLIT" = "dev" ]; then
  echo "Refusing --split dev: dev baselines are M2's sweep (M2/workflows)." >&2
  exit 2
fi

for method in $METHODS; do
  case " $BASELINES " in
    *" $method "*) ;;
    *) echo "Refusing method '$method': only $BASELINES run here." >&2; exit 2 ;;
  esac
done

SYSTEM_FILE="$PROTOCOL_DIR/${SPLIT}_systems.json"
if [ ! -f "$SYSTEM_FILE" ]; then
  echo "No system list for split '$SPLIT': $SYSTEM_FILE does not exist." >&2
  echo "For the hidden split, M1 must add it first (M6/PROTOCOL_ADOPTION.md section 4)." >&2
  exit 2
fi

SYSTEMS="$(python3 -c 'import json,sys; print(" ".join("-".join(s) for s in json.load(open(sys.argv[1]))))' "$SYSTEM_FILE")" || exit 2
if [ -z "$SEEDS" ]; then
  SEEDS="$(python3 -c 'import re,sys; m=re.search(r"seeds:\s*\[([^\]]*)\]", open(sys.argv[1]).read()); print(m.group(1).replace(",", " "))' "$PROTOCOL_DIR/protocol_v1.yaml")" || exit 2
fi
if [ -n "$ONLY_SYSTEMS" ]; then
  for wanted in $ONLY_SYSTEMS; do
    case " $SYSTEMS " in
      *" $wanted "*) ;;
      *) echo "System '$wanted' is not in $SYSTEM_FILE" >&2; exit 2 ;;
    esac
  done
  SYSTEMS="$ONLY_SYSTEMS"
fi

# Prints "completed" if any attempt of the unit finished, else the next free attempt number.
unit_state() {
  local unit_dir="$1" max=0 n entry
  if [ -d "$unit_dir" ]; then
    for entry in "$unit_dir"/attempt_*; do
      [ -e "$entry" ] || continue
      n="$(basename "$entry" | sed -E 's/^attempt_0*([0-9]+).*/\1/')"
      case "$n" in ''|*[!0-9]*) continue ;; esac
      [ "$n" -gt "$max" ] && max="$n"
      if [ -f "$entry/run_metadata.json" ] && \
         python3 -c 'import json,sys; sys.exit(0 if json.load(open(sys.argv[1])).get("status")=="completed" else 1)' "$entry/run_metadata.json" 2>/dev/null; then
        echo "completed:$(basename "$entry")"
        return
      fi
    done
  fi
  echo "next:$((max + 1))"
}

if [ "$EXECUTE" -eq 1 ]; then
  if [ -z "${MATERIALS_PROJECT_API_KEY:-}" ] && [ ! -f "$MADE/.env" ]; then
    echo "MATERIALS_PROJECT_API_KEY is not set and $MADE/.env is missing." >&2
    exit 2
  fi
  command -v uv >/dev/null || { echo "uv is required (cd M1/MADE && uv sync --locked)." >&2; exit 2; }
  LOG_DIR="$SCRIPT_DIR/logs"
  mkdir -p "$LOG_DIR"
  SUMMARY="$LOG_DIR/${SPLIT}_baselines_$(date -u +%Y%m%dT%H%M%SZ).tsv"
  printf 'method\tsplit\tsystem\tseed\tattempt\taction\texit_code\tstarted_utc\tfinished_utc\n' > "$SUMMARY"
fi

total=0; planned=0; skipped=0; failed=0
echo "Split: $SPLIT | systems: $SYSTEMS | seeds: $SEEDS | methods: $METHODS"
[ "$EXECUTE" -eq 1 ] || echo "DRY RUN: nothing will be launched. Add --execute to run."

for method in $METHODS; do
  for system in $SYSTEMS; do
    for seed in $SEEDS; do
      total=$((total + 1))
      unit_dir="$RESULTS_ROOT/$method/$SPLIT/$system/seed_$seed"
      state="$(unit_state "$unit_dir")"
      case "$state" in
        completed:*)
          skipped=$((skipped + 1))
          echo "SKIP  $method $system seed=$seed (${state#completed:} already completed)"
          continue ;;
      esac
      attempt="${state#next:}"
      planned=$((planned + 1))
      cmd="uv run python ../../M2/run_baselines.py --method $method --split $SPLIT --system $system --seed $seed --attempt $attempt"
      echo "RUN   $method $system seed=$seed attempt=$attempt"
      echo "      (cd M1/MADE && $cmd)"
      [ "$EXECUTE" -eq 1 ] || continue

      started="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      (cd "$MADE" && $cmd)
      code=$?
      finished="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      [ "$code" -eq 0 ] || failed=$((failed + 1))
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$method" "$SPLIT" "$system" "$seed" "$attempt" run "$code" "$started" "$finished" >> "$SUMMARY"
      # A failed unit keeps its attempt directory; the loop continues with the next unit.
    done
  done
done

echo "Units: $total | already completed: $skipped | to run: $planned | failed this session: $failed"
[ "$EXECUTE" -eq 1 ] && echo "Summary: $SUMMARY"
[ "$failed" -eq 0 ]
