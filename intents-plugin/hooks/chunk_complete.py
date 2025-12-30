#!/usr/bin/env python3
"""SubagentStop hook: Detect chunk completion marker, validate, auto-commit.

This hook is triggered when a subagent (like feature-implementer) stops.
It checks for a .claude/.chunk-complete marker file, runs validation,
updates MEMORY.md, auto-commits on pass, and cleans up the marker.

Hook event: SubagentStop
Input: JSON on stdin with subagent context
Output: JSON decision (approve/block)
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.checks import run_checks, format_block_reason, get_retry_count, increment_retry_count, reset_retry_count, MAX_RETRIES
from utils.memory import update_chunk_status, add_session_log_entry


MARKER_FILE = '.claude/.chunk-complete'
MARKER_MAX_AGE_SECONDS = 300  # 5 minutes - markers older than this are stale


def approve(message: str = None) -> None:
    """Output approve decision and exit."""
    result = {"decision": "approve"}
    if message:
        result["systemMessage"] = message
    print(json.dumps(result))
    sys.exit(0)


def block(reason: str) -> None:
    """Output block decision and exit."""
    print(json.dumps({
        "decision": "block",
        "reason": reason
    }))
    sys.exit(0)


def read_marker() -> dict | None:
    """Read and parse the chunk complete marker file.

    Returns:
        Parsed marker data, or None if not found/invalid
    """
    if not os.path.exists(MARKER_FILE):
        return None

    try:
        with open(MARKER_FILE, 'r') as f:
            data = json.load(f)

        # Validate required fields
        required = ['chunk', 'feature', 'phase', 'description', 'timestamp']
        if not all(key in data for key in required):
            return None

        # Check if marker is stale (older than max age)
        try:
            marker_time = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            age = (datetime.now(marker_time.tzinfo) - marker_time).total_seconds()
            if age > MARKER_MAX_AGE_SECONDS:
                # Stale marker - delete and ignore
                delete_marker()
                return None
        except Exception:
            pass  # If timestamp parsing fails, proceed anyway

        return data
    except (json.JSONDecodeError, IOError):
        return None


def delete_marker() -> bool:
    """Delete the marker file.

    Returns:
        True if deleted, False on error
    """
    try:
        if os.path.exists(MARKER_FILE):
            os.remove(MARKER_FILE)
        return True
    except IOError:
        return False


def auto_commit(feature: str, chunk: str, description: str) -> tuple[bool, str]:
    """Create an auto-commit for the completed chunk.

    Args:
        feature: Feature name/ID
        chunk: Chunk ID
        description: Chunk description

    Returns:
        Tuple of (success, message)
    """
    try:
        # Stage all changes
        result = subprocess.run(
            ['git', 'add', '-A'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f"git add failed: {result.stderr}"

        # Check if there are changes to commit
        result = subprocess.run(
            ['git', 'diff', '--cached', '--quiet'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            # No changes staged
            return True, "No changes to commit"

        # Create commit
        commit_msg = f"feat({feature}): chunk {chunk} - {description}\n\n[auto-commit by SubagentStop hook]"
        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f"git commit failed: {result.stderr}"

        return True, f"Committed: feat({feature}): chunk {chunk}"
    except subprocess.TimeoutExpired:
        return False, "Git command timed out"
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main hook logic."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # Invalid input, approve to not block workflow
        approve("SubagentStop hook: Invalid input, skipping")
        return

    # CRITICAL: Prevent infinite loops
    if data.get('stop_hook_active'):
        approve()
        return

    # Check for marker file - no marker means this wasn't an implementation subagent
    marker = read_marker()
    if marker is None:
        # No marker = not a chunk completion, just approve
        approve()
        return

    feature = marker['feature']
    chunk = marker['chunk']
    description = marker['description']

    # Check retry limit
    retries = get_retry_count()
    if retries >= MAX_RETRIES:
        reset_retry_count()
        delete_marker()
        approve(f"Chunk {chunk} validation failed {MAX_RETRIES} times. Approving for manual investigation.")
        return

    # Run validation (tests)
    passed, results = run_checks()

    if not passed:
        # Increment retry counter
        increment_retry_count()
        # Block with test output
        reason = format_block_reason(results)
        block(f"Chunk {chunk} validation failed:\n\n{reason}")
        return

    # Validation passed - update MEMORY.md
    update_chunk_status(feature, chunk, 'complete')
    add_session_log_entry(feature, chunk, description)

    # Auto-commit
    commit_success, commit_msg = auto_commit(feature, chunk, description)

    # Clean up
    reset_retry_count()
    delete_marker()

    if commit_success:
        approve(f"Chunk {chunk} complete. {commit_msg}")
    else:
        # Commit failed but validation passed - still approve, just warn
        approve(f"Chunk {chunk} validated but commit failed: {commit_msg}")


if __name__ == '__main__':
    main()
