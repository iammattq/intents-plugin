"""MEMORY.md update operations for chunk completion tracking."""

import re
from pathlib import Path
from typing import Optional

# Import shared utilities from context module (avoid duplication)
from .context import find_memory_file, _validate_feature_name


# Valid chunk ID pattern: digit(s) followed by uppercase letter (e.g., 1A, 2B, 10C)
VALID_CHUNK_PATTERN = re.compile(r'^\d+[A-Z]$')


def _validate_chunk_id(chunk: str) -> bool:
    """Validate chunk ID format.

    Args:
        chunk: Chunk ID to validate (e.g., "1A", "2B")

    Returns:
        True if valid, False otherwise
    """
    if not chunk:
        return False
    return bool(VALID_CHUNK_PATTERN.match(chunk))


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
    # Validate inputs to prevent injection
    if not _validate_feature_name(feature):
        return False
    if not _validate_chunk_id(chunk):
        return False

    memory_path = find_memory_file(feature)
    if not memory_path or not memory_path.exists():
        return False

    try:
        content = memory_path.read_text()

        # Match table row: | chunk | status | anything |
        # Capture everything after status to preserve notes
        # chunk is already validated, so re.escape is safe
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
