#!/bin/zsh

set -u

sweep_repo="/Users/llh/CodexProjects/Group-Project-6-Auto-Research-for-Materials-Discovery"
sweep_expected="27f403c2f554ed4b089915facef021f26fa9b269"
sweep_log="$sweep_repo/M1/MADE/results/protocol_v1/m1_full/dev/reference-sweep-20261025-tmux.log"

exec >> "$sweep_log" 2>&1

sweep_head=$(git -C "$sweep_repo" rev-parse HEAD)
sweep_tag=$(git -C "$sweep_repo" rev-list -n1 m1-freeze-20261025)
if [[ "$sweep_head" != "$sweep_expected" || "$sweep_tag" != "$sweep_expected" ]]; then
  print "FATAL freeze mismatch head=$sweep_head tag=$sweep_tag expected=$sweep_expected"
  exit 2
fi
if [[ -n $(git -C "$sweep_repo" status --porcelain --untracked-files=no) ]]; then
  print "FATAL tracked worktree is not clean"
  exit 3
fi

cd "$sweep_repo/M1/MADE"
sweep_systems=(Mg-Sn-Sr Au-K-Tb Co-Mg-Na Hf-Ni-Zr Co-Dy-W Ga-Pt-Tm)
sweep_seeds=(17 29 43)
sweep_completed=0
sweep_failed=0

print "SWEEP_START $(date -Iseconds) tag=m1-freeze-20261025 commit=$sweep_expected units=18"
for sweep_system in $sweep_systems; do
  for sweep_seed in $sweep_seeds; do
    sweep_seed_dir="results/protocol_v1/m1_full/dev/$sweep_system/seed_$sweep_seed"
    sweep_latest=""
    if [[ -d "$sweep_seed_dir" ]]; then
      sweep_latest=$(find "$sweep_seed_dir" -mindepth 1 -maxdepth 1 -type d -name "attempt_*" | sort | tail -n 1)
    fi
    if [[ -n "$sweep_latest" && -f "$sweep_latest/run_metadata.json" ]]; then
      if ./.venv/bin/python -c 'import json,sys; d=json.load(open(sys.argv[1])); raise SystemExit(0 if d.get("status")=="completed" and d.get("cost",{}).get("oracle",{}).get("queries")==20 else 1)' "$sweep_latest/run_metadata.json"; then
        print "UNIT_SKIP $(date -Iseconds) system=$sweep_system seed=$sweep_seed path=$sweep_latest"
        sweep_completed=$((sweep_completed + 1))
        continue
      fi
    fi

    sweep_attempt=1
    while [[ -e "$sweep_seed_dir/attempt_$(printf %02d $sweep_attempt)" ]]; do
      sweep_attempt=$((sweep_attempt + 1))
    done
    print "UNIT_START $(date -Iseconds) system=$sweep_system seed=$sweep_seed attempt=$sweep_attempt"
    if ./.venv/bin/python ../run_experiment.py --method m1_full --split dev --system "$sweep_system" --seed "$sweep_seed" --attempt "$sweep_attempt"; then
      print "UNIT_OK $(date -Iseconds) system=$sweep_system seed=$sweep_seed attempt=$sweep_attempt"
      sweep_completed=$((sweep_completed + 1))
    else
      sweep_code=$?
      print "UNIT_FAIL $(date -Iseconds) system=$sweep_system seed=$sweep_seed attempt=$sweep_attempt exit=$sweep_code"
      sweep_failed=$((sweep_failed + 1))
    fi
  done
done

print "SWEEP_END $(date -Iseconds) completed=$sweep_completed failed=$sweep_failed"
[[ $sweep_failed -eq 0 && $sweep_completed -eq 18 ]]
