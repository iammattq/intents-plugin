#!/usr/bin/env python3
"""Stop hook: Auto-detect and run tests, block on failure.

This hook runs when Claude Code is about to stop and performs quality
checks (tests) to validate work before completion.

Key features:
- Auto-detects project type and test command
- Prevents infinite loops via stop_hook_active check
- 3-retry limit to prevent stuck states
- Includes test output in block reasons
- Fails open (approves) on errors

Usage in .claude/settings.json:
{
  "hooks": {
    "Stop": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 intents-plugin/hooks/feature_complete.py"
      }]
    }]
  }
}
"""

import json
import sys
import os

# Add hooks directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hooks.utils.checks import (
    get_test_command,
    run_checks,
    format_block_reason,
    get_retry_count,
    increment_retry_count,
    reset_retry_count,
    check_retry_limit,
    MAX_RETRIES,
)


def approve(message: str = None):
    """Output approve decision and exit."""
    result = {"decision": "approve"}
    if message:
        result["systemMessage"] = message
    print(json.dumps(result))
    sys.exit(0)


def block(reason: str):
    """Output block decision and exit."""
    print(json.dumps({
        "decision": "block",
        "reason": reason
    }))
    sys.exit(0)


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # No input or invalid JSON - approve and continue (fail open)
        approve()
        return

    # CRITICAL: Prevent infinite loops
    # If stop_hook_active is True, this hook was triggered by a previous
    # block, so we must approve to prevent loops
    if data.get('stop_hook_active'):
        approve()
        return

    # Check retry limit before running checks
    exceeded, count = check_retry_limit()
    if exceeded:
        reset_retry_count()
        approve(f"Quality checks failed {MAX_RETRIES} times. Approving to allow manual investigation.")
        return

    # Check if there's a test command for this project
    test_cmd = get_test_command()
    if test_cmd is None:
        # No test command detected - approve (can't validate)
        approve()
        return

    # Run quality checks
    try:
        passed, results = run_checks()
    except Exception as e:
        # Error running checks - fail open (approve)
        approve(f"Error running quality checks: {str(e)}")
        return

    if passed:
        # All checks passed - reset retry count and approve
        reset_retry_count()
        approve("Quality checks passed.")
        return

    # Checks failed - increment retry count and block
    new_count = increment_retry_count()
    remaining = MAX_RETRIES - new_count

    reason = format_block_reason(results)
    if remaining > 0:
        reason += f"\n\n(Attempt {new_count}/{MAX_RETRIES}. {remaining} retries remaining before auto-approve.)"
    else:
        reason += f"\n\n(Final attempt. Will auto-approve on next failure.)"

    block(reason)


if __name__ == "__main__":
    main()
