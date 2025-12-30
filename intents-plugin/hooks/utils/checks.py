"""Test command detection and execution utilities."""

import fcntl
import os
import subprocess
from typing import Optional, Tuple, List, Dict, Any


# Retry tracking file location
RETRY_FILE = '.claude/.hook-retries'
RETRY_LOCK_FILE = '.claude/.hook-retries.lock'
MAX_RETRIES = 3


def get_test_command() -> Optional[List[str]]:
    """Auto-detect test command based on project type.

    Returns:
        Test command as list of args if detected, None otherwise
    """
    if os.path.exists('package.json'):
        return ['npm', 'test']
    elif os.path.exists('pyproject.toml') or os.path.exists('setup.py'):
        return ['pytest']
    elif os.path.exists('Cargo.toml'):
        return ['cargo', 'test']
    return None  # Skip validation if unknown project type


def run_checks(timeout: int = 120) -> Tuple[bool, List[Dict[str, Any]]]:
    """Run quality checks (tests) and return results.

    Args:
        timeout: Maximum seconds to wait for tests

    Returns:
        Tuple of (all_passed, results_list)
        results_list contains dicts with name, passed, output
    """
    cmd = get_test_command()
    if cmd is None:
        # No tests to run, pass by default
        return True, []

    try:
        # Use list form without shell=True to prevent injection
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        passed = result.returncode == 0
        output = result.stdout + result.stderr
        return passed, [{
            "name": "test",
            "passed": passed,
            "output": output
        }]
    except subprocess.TimeoutExpired:
        return False, [{
            "name": "test",
            "passed": False,
            "output": f"Tests timed out after {timeout} seconds"
        }]
    except Exception as e:
        return False, [{
            "name": "test",
            "passed": False,
            "output": f"Error running tests: {str(e)}"
        }]


def format_block_reason(results: List[Dict[str, Any]]) -> str:
    """Format test results into a block reason with actionable feedback.

    Args:
        results: List of test result dicts from run_checks

    Returns:
        Formatted string explaining failures
    """
    lines = ["Quality checks failed:\n"]
    for r in results:
        status = "[PASS]" if r["passed"] else "[FAIL]"
        lines.append(f"{status} {r['name']}")
        if not r["passed"]:
            # Truncate output to first 500 chars to keep message readable
            output = r.get("output", "")
            if len(output) > 500:
                output = output[:500] + "\n... (truncated)"
            lines.append(f"\nOutput:\n{output}")
    lines.append("\nPlease fix the failing checks.")
    return "\n".join(lines)


def _with_lock(func):
    """Decorator to run function with file lock for atomic operations."""
    def wrapper(*args, **kwargs):
        os.makedirs(os.path.dirname(RETRY_LOCK_FILE), exist_ok=True)
        try:
            with open(RETRY_LOCK_FILE, 'w') as lock_file:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
                try:
                    return func(*args, **kwargs)
                finally:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        except IOError:
            # If locking fails, still try to run the function
            return func(*args, **kwargs)
    return wrapper


@_with_lock
def get_retry_count() -> int:
    """Get current retry count from tracking file.

    Returns:
        Number of retries so far (0 if file doesn't exist)
    """
    try:
        if os.path.exists(RETRY_FILE):
            with open(RETRY_FILE, 'r') as f:
                return int(f.read().strip())
    except (ValueError, IOError):
        pass
    return 0


@_with_lock
def increment_retry_count() -> int:
    """Increment and persist retry count (atomic with file lock).

    Returns:
        New retry count
    """
    # Re-read inside lock to ensure atomicity
    count = 0
    try:
        if os.path.exists(RETRY_FILE):
            with open(RETRY_FILE, 'r') as f:
                count = int(f.read().strip())
    except (ValueError, IOError):
        pass

    count += 1
    try:
        os.makedirs(os.path.dirname(RETRY_FILE), exist_ok=True)
        with open(RETRY_FILE, 'w') as f:
            f.write(str(count))
    except IOError:
        pass
    return count


@_with_lock
def reset_retry_count() -> None:
    """Reset retry count (delete tracking file)."""
    try:
        if os.path.exists(RETRY_FILE):
            os.remove(RETRY_FILE)
    except IOError:
        pass


def check_retry_limit() -> Tuple[bool, int]:
    """Check if retry limit has been exceeded.

    Returns:
        Tuple of (exceeded, current_count)
    """
    count = get_retry_count()
    return count >= MAX_RETRIES, count
