"""MEMORY.md update operations for chunk completion tracking."""

import re
from pathlib import Path
from glob import glob
from typing import Optional


def find_memory_file(feature: str) -> Optional[Path]:
    """Find MEMORY.md for the given feature.

    Args:
        feature: Feature name/ID to search for

    Returns:
        Path to MEMORY.md if found, None otherwise
    """
    patterns = [
        f'docs/plans/{feature}/MEMORY.md',
        f'docs/plans/*/{feature}/MEMORY.md',  # Enhancement path
    ]
    for pattern in patterns:
        matches = glob(pattern)
        if matches:
            return Path(matches[0])
    return None


def update_chunk_status(feature: str, chunk: str, status: str = 'complete') -> bool:
    """Update chunk status in MEMORY.md progress table.

    Looks for table rows like:
        | 1A | pending | Notes |
    And updates to:
        | 1A | complete | Notes |

    Args:
        feature: Feature name/ID
        chunk: Chunk ID (e.g., "1A", "2B")
        status: New status (default: "complete")

    Returns:
        True if update was made, False otherwise
    """
    memory_path = find_memory_file(feature)
    if not memory_path or not memory_path.exists():
        return False

    try:
        content = memory_path.read_text()

        # Match table row: | chunk | status | anything |
        # Capture everything after status to preserve notes
        pattern = rf'(\|\s*{re.escape(chunk)}\s*\|)\s*\w+\s*(\|.*)'
        replacement = rf'\1 {status} \2'
        updated = re.sub(pattern, replacement, content)

        if updated != content:
            memory_path.write_text(updated)
            return True
        return False
    except Exception:
        return False


def add_session_log_entry(feature: str, chunk: str, description: str) -> bool:
    """Add a session log entry for chunk completion.

    Appends to the Session Log section with timestamp and chunk info.

    Args:
        feature: Feature name/ID
        chunk: Chunk ID that was completed
        description: Description of what was completed

    Returns:
        True if entry was added, False otherwise
    """
    memory_path = find_memory_file(feature)
    if not memory_path or not memory_path.exists():
        return False

    try:
        from datetime import datetime
        content = memory_path.read_text()

        # Find "## Session Log" section and add entry after it
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        entry = f"\n### {timestamp} - Chunk {chunk} Auto-Commit\n\n**Completed:** {description}\n\n*Auto-committed by SubagentStop hook.*\n"

        # Insert after "## Session Log" line
        if '## Session Log' in content:
            content = content.replace(
                '## Session Log\n',
                f'## Session Log\n{entry}',
                1
            )
            memory_path.write_text(content)
            return True
        return False
    except Exception:
        return False


def get_current_phase(feature: str) -> Optional[int]:
    """Get current phase number from MEMORY.md.

    Args:
        feature: Feature name/ID

    Returns:
        Current phase number, or None if not found
    """
    memory_path = find_memory_file(feature)
    if not memory_path or not memory_path.exists():
        return None

    try:
        content = memory_path.read_text()
        # Look for "Current Phase: Phase N" pattern
        match = re.search(r'\*\*Current Phase:\*\*\s*Phase\s*(\d+)', content)
        if match:
            return int(match.group(1))
        return None
    except Exception:
        return None
