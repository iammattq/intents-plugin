"""Graph.yaml operations for feature status updates."""

import re
from pathlib import Path
from typing import Optional


GRAPH_PATH = '.intents/graph.yaml'


def find_graph_file() -> Optional[Path]:
    """Find the graph.yaml file.

    Returns:
        Path to graph.yaml if found, None otherwise
    """
    path = Path(GRAPH_PATH)
    if path.exists():
        return path
    return None


def update_graph_status(feature: str, status: str) -> bool:
    """Update feature status in graph.yaml.

    Updates the status field for the given feature node.

    Args:
        feature: Feature name/ID
        status: New status (e.g., 'implemented', 'in-progress', 'broken')

    Returns:
        True if update was made, False otherwise
    """
    graph_path = find_graph_file()
    if not graph_path:
        return False

    try:
        content = graph_path.read_text()

        # Pattern to match the feature block and update status
        # Matches:
        #   feature-name:
        #     status: old-status
        # And replaces with new status
        pattern = rf'(^{re.escape(feature)}:\s*\n(?:[ \t]+[^\n]+\n)*?[ \t]+status:)\s*\S+'
        replacement = rf'\1 {status}'

        updated = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        if updated != content:
            graph_path.write_text(updated)
            return True
        return False
    except Exception:
        return False


def get_feature_status(feature: str) -> Optional[str]:
    """Get current status of a feature from graph.yaml.

    Args:
        feature: Feature name/ID

    Returns:
        Status string if found, None otherwise
    """
    graph_path = find_graph_file()
    if not graph_path:
        return None

    try:
        content = graph_path.read_text()

        # Pattern to find feature and extract status
        pattern = rf'^{re.escape(feature)}:\s*\n(?:[ \t]+[^\n]+\n)*?[ \t]+status:\s*(\S+)'
        match = re.search(pattern, content, flags=re.MULTILINE)

        if match:
            return match.group(1)
        return None
    except Exception:
        return None


def is_feature_complete(feature: str) -> bool:
    """Check if a feature is marked as completing (all phases done).

    Checks MEMORY.md for indicators that all phases are complete:
    - All phase chunks marked complete
    - Current phase is the last phase
    - Status indicates completion

    Args:
        feature: Feature name/ID

    Returns:
        True if feature appears to be completing
    """
    from .memory import find_memory_file

    memory_path = find_memory_file(feature)
    if not memory_path or not memory_path.exists():
        return False

    try:
        content = memory_path.read_text()

        # Check 1: Look for completion indicators in status
        if re.search(r'\*\*Status:\*\*\s*(complete|done|finished)', content, re.IGNORECASE):
            return True

        # Check 2: Look for "all phases complete" patterns
        if re.search(r'all\s+phases?\s+(are\s+)?complete', content, re.IGNORECASE):
            return True

        # Check 3: Count pending vs complete phases
        # Match phase rows: | Phase N: Name | status |
        phase_pattern = r'\|\s*Phase\s*\d+[^|]*\|\s*(\w+)\s*\|'
        phase_statuses = re.findall(phase_pattern, content, re.IGNORECASE)

        if phase_statuses:
            pending = sum(1 for s in phase_statuses if s.lower() in ('pending', 'in-progress'))
            if pending == 0:
                return True

        # Check 4: Check if we're on final phase and it's complete
        # Look for "Current Phase: Phase N" and compare with total phases
        current_match = re.search(r'\*\*Current Phase:\*\*\s*Phase\s*(\d+)', content)
        if current_match:
            current_phase = int(current_match.group(1))
            # Count total phases mentioned
            total_phases = len(set(re.findall(r'Phase\s*(\d+)', content)))
            # If current is >= total and has "complete" nearby, likely finishing
            if current_phase >= total_phases:
                # Check if the current phase section shows complete
                phase_section = re.search(
                    rf'Phase\s*{current_phase}[^|]*\|\s*(complete|done)',
                    content,
                    re.IGNORECASE
                )
                if phase_section:
                    return True

        return False
    except Exception:
        return False
