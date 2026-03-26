#!/bin/bash
# Pattern: Verification & Evals (PostToolUse hook) | Principle: P5 | Tool: Claude Code CLI
#
# This hook runs after Claude writes or edits a file (PostToolUse lifecycle event).
# It runs your type checker or test suite automatically.
# Exit code 2 blocks Claude from continuing — Claude sees the output and self-corrects.
#
# Register in ~/.claude/settings.json:
#   "hooks": {
#     "PostToolUse": [{
#       "matcher": "Write|Edit",
#       "command": "bash ~/.claude/hooks/post-tool-verify.sh"
#     }]
#   }
#
# Claude Code CLI only — PostToolUse hooks are not available in VS Code extension.

set -euo pipefail

# Read tool event from stdin
INPUT=$(cat)
FILE=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('file_path',''))" 2>/dev/null || echo "")

if [[ -z "$FILE" ]]; then
  exit 0  # No file path in event — proceed normally
fi

# Detect language and run appropriate checker
if [[ "$FILE" == *.ts || "$FILE" == *.tsx ]]; then
  echo "→ TypeScript check after editing $FILE"
  npx tsc --noEmit 2>&1
  STATUS=$?
  if [[ $STATUS -ne 0 ]]; then
    echo "TypeScript errors found. Fix them before continuing."
    exit 2  # Blocks Claude — it will see this output and fix the errors
  fi

elif [[ "$FILE" == *.py ]]; then
  echo "→ Python check after editing $FILE"
  # Run mypy if available, otherwise skip
  if command -v mypy &>/dev/null; then
    mypy "$FILE" --ignore-missing-imports 2>&1 | tail -10
    if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
      echo "Type errors found. Fix them before continuing."
      exit 2
    fi
  fi

elif [[ "$FILE" == *.go ]]; then
  echo "→ Go vet after editing $FILE"
  go vet ./... 2>&1
  if [[ $? -ne 0 ]]; then
    echo "Go vet errors found. Fix them before continuing."
    exit 2
  fi
fi

# exit 0 = Claude proceeds normally
exit 0
