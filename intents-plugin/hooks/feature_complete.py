#!/usr/bin/env python3
"""Stop hook: Final validation at feature completion.

This hook runs when Claude Code is about to stop and performs:
1. Quality checks (tests) to validate work
2. Plan verification (compare implementation to PLAN.md requirements)
3. Code review spawning (on feature completion)
4. Graph status update (set to 'implemented' on full pass)

Key features:
- Auto-detects project type and test command
- Verifies implementation against PLAN.md requirements
- Spawns code-reviewer at feature completion
- Updates graph.yaml status on success
- Prevents infinite loops via stop_hook_active check
- 3-retry limit to prevent stuck states
- Includes test/verification output in block reasons
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
from hooks.utils.context import get_current_feature, find_plan_file
from hooks.utils.plan_verify import verify_implementation, format_verification_failures
from hooks.utils.graph import update_graph_status, is_feature_complete


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


def detect_feature_completion(feature: str) -> bool:
    """Detect if a feature is completing (all phases done).

    Checks MEMORY.md for completion indicators.

    Args:
        feature: Feature name/ID

    Returns:
        True if feature appears to be completing
    """
    if not feature:
        return False
    return is_feature_complete(feature)


def spawn_code_review(feature: str) -> dict:
    """Spawn code-reviewer agent for final review.

    Returns result with passed status and output.

    Args:
        feature: Feature name/ID

    Returns:
        Dict with 'passed' and 'output' keys
    """
    import subprocess

    try:
        # Get changed files for the feature
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'main...HEAD'],
            capture_output=True, text=True, timeout=30
        )
        changed_files = result.stdout.strip()

        if not changed_files:
            return {'passed': True, 'output': 'No changed files to review.'}

        # Code review is handled by the /implement command's review stage
        # This hook just signals that review should happen (not blocking)
        return {
            'passed': True,
            'output': f'Code review skipped (handled by /implement command). Files changed:\n{changed_files}'
        }
    except Exception as e:
        return {'passed': True, 'output': f'Could not determine changed files: {e}'}


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

    # Detect current feature
    feature = get_current_feature()

    # Track all validation results
    all_results = []
    all_passed = True

    # === Step 1: Run quality checks (tests) ===
    test_cmd = get_test_command()
    if test_cmd is not None:
        try:
            passed, results = run_checks()
            all_results.extend(results)
            if not passed:
                all_passed = False
        except Exception as e:
            # Error running checks - log but continue
            all_results.append({
                'name': 'test',
                'passed': False,
                'output': f'Error running tests: {str(e)}'
            })
            all_passed = False

    # === Step 2: Plan verification (if feature detected) ===
    if feature:
        plan_path = find_plan_file(feature)
        if plan_path and plan_path.exists():
            try:
                verification = verify_implementation(feature)
                if not verification['passed']:
                    all_passed = False
                    all_results.append({
                        'name': 'plan-verification',
                        'passed': False,
                        'output': format_verification_failures(verification)
                    })
                else:
                    all_results.append({
                        'name': 'plan-verification',
                        'passed': True,
                        'output': 'Implementation matches PLAN.md requirements.'
                    })
            except Exception as e:
                # Plan verification failed - log but don't block
                all_results.append({
                    'name': 'plan-verification',
                    'passed': True,  # Fail open
                    'output': f'Could not verify plan: {str(e)}'
                })

    # === Step 3: Feature completion handling ===
    if feature and all_passed and detect_feature_completion(feature):
        # Feature is completing - spawn code review
        review_result = spawn_code_review(feature)
        all_results.append({
            'name': 'code-review',
            'passed': review_result['passed'],
            'output': review_result['output']
        })

        if review_result['passed']:
            # Update graph status to implemented
            try:
                update_graph_status(feature, 'implemented')
            except Exception as e:
                # Graph update failed - log to stderr but don't block workflow
                import sys
                print(f"Warning: Graph update failed for {feature}: {e}", file=sys.stderr)

    # === Final decision ===
    if all_passed:
        reset_retry_count()
        if feature:
            approve(f"All checks passed for feature: {feature}")
        else:
            approve("Quality checks passed.")
        return

    # Checks failed - increment retry count and block
    new_count = increment_retry_count()
    remaining = MAX_RETRIES - new_count

    reason = format_block_reason(all_results)
    if remaining > 0:
        reason += f"\n\n(Attempt {new_count}/{MAX_RETRIES}. {remaining} retries remaining before auto-approve.)"
    else:
        reason += f"\n\n(Final attempt. Will auto-approve on next failure.)"

    block(reason)


if __name__ == "__main__":
    main()
