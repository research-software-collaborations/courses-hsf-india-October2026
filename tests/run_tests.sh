#!/bin/bash
# Run all package tests and report a summary including GPU status per package.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

declare -a PASS=()
declare -a FAIL=()
declare -A GPU_STATUS=()

run_test() {
    local script="$1"
    local name
    name=$(basename "$script" .py)
    echo "========================================"
    echo "Running $name ..."
    echo "----------------------------------------"
    local output
    if output=$(python "$script" 2>&1); then
        PASS+=("$name")
        echo "$output"
    else
        FAIL+=("$name")
        echo "$output"
    fi
    # capture the GPU: line if present
    local gpu_line
    gpu_line=$(echo "$output" | grep -m1 '^GPU:' | sed 's/^GPU: //' || true)
    GPU_STATUS["$name"]="${gpu_line:-n/a}"
}

for f in "$SCRIPT_DIR"/test_*.py; do
    run_test "$f"
done

echo ""
echo "========================================"
echo "SUMMARY"
echo "========================================"
printf "%-30s %-8s %s\n" "TEST" "RESULT" "GPU"
echo "----------------------------------------"
for name in "${PASS[@]}" "${FAIL[@]}"; do
    result="PASS"
    [[ " ${FAIL[*]} " == *" $name "* ]] && result="FAIL"
    printf "%-30s %-8s %s\n" "$name" "$result" "${GPU_STATUS[$name]:-n/a}"
done
echo "========================================"
echo "Passed: ${#PASS[@]}  Failed: ${#FAIL[@]}"
echo "========================================"

[ ${#FAIL[@]} -eq 0 ]
