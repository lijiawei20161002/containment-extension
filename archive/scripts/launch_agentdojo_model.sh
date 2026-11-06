#!/bin/bash
# Usage: launch_agentdojo_model.sh <model> <logdir> <suite:budget> [<suite:budget> ...]
# Generates grants per suite first, then runs every arm over the suites sequentially (one process per arm).
set -u
B="$(cd "$(dirname "$0")/.." && pwd)"
MODEL=$1; L=$2; shift 2
SUITES=("$@")
mkdir -p "$L/logs"
for sb in "${SUITES[@]}"; do
  s=${sb%%:*}
  "$B/.venv/bin/python" "$B/scripts/run_agentdojo_grant.py" --suite "$s" --model "$MODEL" --arm grant_broker --generate-grants --budget-usd 5 --logdir "$L" >> "$L/logs/grants-$s.log" 2>&1 || echo "grant generation failed for $s" >> "$L/logs/grants-$s.log"
done
run_arm() {  # name, arm, extra flags
  name=$1; arm=$2; shift 2
  (
    for sb in "${SUITES[@]}"; do
      s=${sb%%:*}; budget=${sb##*:}
      for i in 1 2 3 4; do
        "$B/.venv/bin/python" "$B/scripts/run_agentdojo_grant.py" --suite "$s" --model "$MODEL" --arm "$arm" "$@" --benign --budget-usd "$budget" --logdir "$L" >> "$L/logs/$name-$s.log" 2>&1 && break
        echo "RETRY $i" >> "$L/logs/$name-$s.log"; sleep 60
      done
      echo DONE >> "$L/logs/$name-$s.log"
    done
  ) &
}
run_arm none none
run_arm repeat_user_prompt repeat_user_prompt
run_arm spotlighting spotlighting_with_delimiting
run_arm grant_broker grant_broker
run_arm grant_broker_narrow grant_broker --update narrow
run_arm effect_journal effect_journal
run_arm grant_advice grant_advice
wait
echo "ALL ARMS DONE for $MODEL" >> "$L/logs/all.log"
