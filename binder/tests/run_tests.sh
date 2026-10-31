#!/bin/bash
# Run all package tests and report a summary.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=()
FAIL=()

run_test() {
    local script="$1"
    local name
    name=$(basename "$script" .py)
    echo "========================================"
    echo "Running $name ..."
    echo "----------------------------------------"
    if python "$script"; then
        PASS+=("$name")
    else
        FAIL+=("$name")
    fi
}

for f in "$SCRIPT_DIR"/test_*.py; do
    run_test "$f"
done

echo ""
echo "========================================"
echo "SUMMARY"
echo "========================================"
echo "PASSED (${#PASS[@]}): ${PASS[*]:-none}"
echo "FAILED (${#FAIL[@]}): ${FAIL[*]:-none}"
echo "========================================"

[ ${#FAIL[@]} -eq 0 ]
