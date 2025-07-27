#!/usr/bin/env bash
# Summarize gem5 stats into a CSV (IPC + branch accuracy if available).
# Usage:
#   ./report-gen.sh                         # uses default OUT_DIR
#   ./report-gen.sh /custom/path/to/out     # override OUT_DIR

set -euo pipefail

# ---- Config (change if needed) ----
OUT_DIR_DEFAULT="/Users/rezashrestha/Documents/MSCS-531/Week5/gem5-ilp-project/out"
OUT_DIR="${1:-$OUT_DIR_DEFAULT}"
CSV="${OUT_DIR}/results.csv"

# ---- Safety / UX ----
if [[ ! -d "$OUT_DIR" ]]; then
  echo "ERROR: OUT_DIR not found: $OUT_DIR" >&2
  exit 1
fi

# Enable nullglob so */stats.txt expands to nothing if absent
shopt -s nullglob

echo "run,committedInsts,numCycles,IPC,branch_lookups,branch_incorrect,branch_accuracy_percent" > "$CSV"

# Loop over immediate subdirs that contain stats.txt (e.g., out/compute_loop/stats.txt)
found_any=0
for stats in "$OUT_DIR"/*/stats.txt; do
  run="$(basename "$(dirname "$stats")")"
  awk -v run="$run" '
    # Try multiple instruction counters (first one wins)
    /(^|\.)committedInsts[[:space:]]/ && ins=="" {ins=$2}
    /(^|\.)numInsts[[:space:]]/       && ins=="" {ins=$2}
    /^simInsts[[:space:]]/            && ins=="" {ins=$2}

    # Cycles (common) and direct IPC (sometimes present)
    /(^|\.)numCycles[[:space:]]/ {cyc=$2}
    /(^|\.)ipc[[:space:]]/       {ipc_stat=$2}

    # Branch predictor counters (names vary by build)
    /branchPred\.lookups[[:space:]]/                             {L=$2}
    /branchPred\.(incorrect|mispred|condIncorrect|condMispredicted)[[:space:]]/ {M=$2}

    END{
      ipc = 0
      if (ins != "" && cyc > 0) ipc = ins/cyc
      else if (ipc_stat != "")  ipc = ipc_stat

      acc = (L > 0 ? 100*(1 - M/L) : "")

      printf("%s,%s,%s,%.6f,%s,%s,%s\n",
             run,
             (ins==""?0:ins)+0,
             (cyc==""?0:cyc)+0,
             ipc,
             (L==""?"":L),
             (M==""?"":M),
             (acc==""?"":acc))
    }
  ' "$stats" >> "$CSV"
  found_any=1
done

if [[ "$found_any" -eq 0 ]]; then
  echo "No stats.txt found under: $OUT_DIR" >&2
  exit 2
fi

# Pretty print to terminal if `column` exists
if command -v column >/dev/null 2>&1; then
  column -t -s, "$CSV" || true
else
  cat "$CSV"
fi

echo "Wrote: $CSV"
