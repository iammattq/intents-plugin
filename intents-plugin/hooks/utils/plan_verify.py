"""Plan verification utilities - compare implementation to PLAN.md requirements."""

import re
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import shared utilities from context module (avoid duplication)
from .context import find_plan_file, find_memory_file


def extract_ship_criteria(plan_content: str) -> List[str]:
    """Extract ship criteria from PLAN.md content.

    Looks for patterns like:
    - [ ] Criteria description
    - [x] Completed criteria

    In the "Ship Criteria" section.

    Args:
        plan_content: Content of PLAN.md

    Returns:
        List of criteria strings
    """
    criteria = []

    # Find Ship Criteria section(s)
    # Match both "**Ship Criteria:**" and "## Ship Criteria" patterns
    ship_section_pattern = r'(?:\*\*Ship Criteria[:\*]*|##\s*Ship Criteria)[^\n]*\n((?:[-*]\s*\[[ x]\][^\n]+\n?)+)'
    matches = re.findall(ship_section_pattern, plan_content, re.IGNORECASE | re.MULTILINE)

    for match in matches:
        # Extract individual criteria items
        item_pattern = r'[-*]\s*\[[ x]\]\s*(.+?)(?:\n|$)'
        items = re.findall(item_pattern, match)
        criteria.extend(items)

    return criteria


def extract_checked_criteria(memory_content: str) -> List[str]:
    """Extract completed criteria from MEMORY.md.

    Looks for patterns like:
    - [x] Completed criteria

    Args:
        memory_content: Content of MEMORY.md

    Returns:
        List of completed criteria strings
    """
    completed = []

    # Match checked items
    pattern = r'[-*]\s*\[x\]\s*(.+?)(?:\n|$)'
    items = re.findall(pattern, memory_content, re.IGNORECASE)
    completed.extend(items)

    return completed


def verify_implementation(feature: str) -> Dict[str, Any]:
    """Verify implementation against PLAN.md requirements.

    Compares ship criteria in PLAN.md with completed items in MEMORY.md.

    Args:
        feature: Feature name/ID

    Returns:
        Dict with:
            - passed: bool - True if all criteria met
            - total: int - Total criteria count
            - completed: int - Completed criteria count
            - missing: List[str] - List of unmet criteria
    """
    result = {
        'passed': True,
        'total': 0,
        'completed': 0,
        'missing': []
    }

    # Load plan
    plan_path = find_plan_file(feature)
    if not plan_path or not plan_path.exists():
        # No plan found - can't verify, pass by default
        return result

    try:
        plan_content = plan_path.read_text()
    except Exception:
        return result

    # Load memory
    memory_path = find_memory_file(feature)
    memory_content = ""
    if memory_path and memory_path.exists():
        try:
            memory_content = memory_path.read_text()
        except Exception:
            pass

    # Extract criteria from plan
    criteria = extract_ship_criteria(plan_content)
    result['total'] = len(criteria)

    if not criteria:
        # No criteria found - can't verify, pass by default
        return result

    # Extract completed items from memory
    completed = extract_checked_criteria(memory_content)

    # Normalize for comparison (lowercase, strip whitespace)
    def normalize(s: str) -> str:
        return s.lower().strip()

    completed_normalized = set(normalize(c) for c in completed)

    # Check each criterion
    for criterion in criteria:
        criterion_normalized = normalize(criterion)
        # Check if this criterion is in completed list (fuzzy match)
        found = False
        for comp in completed_normalized:
            # Check if criterion text is contained in completed item or vice versa
            if criterion_normalized in comp or comp in criterion_normalized:
                found = True
                break
            # Also check for high word overlap
            criterion_words = set(criterion_normalized.split())
            comp_words = set(comp.split())
            if len(criterion_words & comp_words) >= len(criterion_words) * 0.7:
                found = True
                break

        if found:
            result['completed'] += 1
        else:
            result['missing'].append(criterion)

    result['passed'] = len(result['missing']) == 0

    return result


def format_verification_failures(result: Dict[str, Any]) -> str:
    """Format verification failures as readable output.

    Args:
        result: Result from verify_implementation()

    Returns:
        Formatted string describing failures
    """
    lines = []
    lines.append(f"Plan verification: {result['completed']}/{result['total']} criteria met")

    if result['missing']:
        lines.append("\nMissing ship criteria:")
        for item in result['missing']:
            lines.append(f"  - [ ] {item}")

    lines.append("\nPlease complete the missing criteria before finishing.")

    return "\n".join(lines)
