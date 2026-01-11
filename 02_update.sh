#!/bin/bash
# update.sh - Consolidate acrodefs.tex files and update GitHub Gist
#
# This script:
# 1. Reads all acrodefs.tex files listed in list.txt
# 2. Consolidates and deduplicates the definitions
# 3. Updates the GitHub Gist with the consolidated file

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GIST_ID="169753e43f3ef938c0db1410ffd34a44"
OUTPUT_FILE="acrodefs.tex"
CONSOLIDATE_SCRIPT="consolidate.py"

echo "=== Consolidating acrodefs.tex files ==="
echo

# Run the consolidation script
if [ ! -f "$CONSOLIDATE_SCRIPT" ]; then
    echo "Error: $CONSOLIDATE_SCRIPT not found"
    exit 1
fi

python3.12 "$CONSOLIDATE_SCRIPT"

# Check if consolidation was successful
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Consolidated file $OUTPUT_FILE was not created"
    exit 1
fi

echo
echo "=== Updating GitHub Gist ==="
echo

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Update the Gist
gh gist edit "$GIST_ID" -a "$OUTPUT_FILE"

if [ $? -eq 0 ]; then
    echo
    echo "=== Update complete! ==="
    echo "Gist URL: https://gist.github.com/larsvilhuber/$GIST_ID"
    echo "Lines in consolidated file: $(wc -l < "$OUTPUT_FILE")"
else
    echo "Error: Failed to update Gist"
    exit 1
fi
