"""Context loading utilities for MEMORY.md and PLAN.md."""

import os
import re
from pathlib import Path
from glob import glob
from typing import Optional, Tuple


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


def find_plan_file(feature: str) -> Optional[Path]:
    """Find PLAN.md for the given feature.

    Args:
        feature: Feature name/ID to search for

    Returns:
        Path to PLAN.md if found, None otherwise
    """
    patterns = [
        f'docs/plans/{feature}/PLAN.md',
        f'docs/plans/*/{feature}/PLAN.md',  # Enhancement path
    ]
    for pattern in patterns:
        matches = glob(pattern)
        if matches:
            return Path(matches[0])
    return None


def get_current_feature() -> Optional[str]:
    """Detect current in-progress feature from git branch or MEMORY.md files.

    Returns:
        Feature name if detected, None otherwise
    """
    # Try git branch first (feature/name pattern)
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            # Match feature/name or feature/name-with-dashes
            match = re.match(r'^feature/(.+)$', branch)
            if match:
                return match.group(1)
    except Exception:
        pass

    # Fallback: look for any in-progress MEMORY.md
    for memory_path in glob('docs/plans/*/MEMORY.md'):
        try:
            content = Path(memory_path).read_text()
            # Check if status indicates in-progress
            if re.search(r'\*\*Status:\*\*\s*(in[- ]?progress|implementing)', content, re.IGNORECASE):
                # Extract feature from path
                parts = Path(memory_path).parts
                if len(parts) >= 3:
                    return parts[-2]  # docs/plans/<feature>/MEMORY.md
        except Exception:
            continue

    return None


def load_context(feature: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """Load MEMORY.md and PLAN.md content for context injection.

    Args:
        feature: Feature name (auto-detected if not provided)

    Returns:
        Tuple of (memory_content, plan_content), either can be None
    """
    if feature is None:
        feature = get_current_feature()

    if feature is None:
        return None, None

    memory_content = None
    plan_content = None

    memory_path = find_memory_file(feature)
    if memory_path and memory_path.exists():
        try:
            memory_content = memory_path.read_text()
        except Exception:
            pass

    plan_path = find_plan_file(feature)
    if plan_path and plan_path.exists():
        try:
            plan_content = plan_path.read_text()
        except Exception:
            pass

    return memory_content, plan_content


def format_context_message(memory_content: Optional[str], plan_content: Optional[str], feature: str) -> str:
    """Format context as a system message for Claude.

    Args:
        memory_content: Content of MEMORY.md
        plan_content: Content of PLAN.md
        feature: Feature name

    Returns:
        Formatted system message
    """
    lines = [f"Resuming in-progress feature: {feature}\n"]

    if memory_content:
        lines.append("## Current State (MEMORY.md)\n")
        lines.append(memory_content)
        lines.append("")

    if plan_content:
        lines.append("## Implementation Plan (PLAN.md)\n")
        lines.append(plan_content)

    return "\n".join(lines)
