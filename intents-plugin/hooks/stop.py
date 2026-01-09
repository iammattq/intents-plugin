#!/usr/bin/env python3
"""
Stop hook for intents-plugin token tracking.

Updates token counts and displays elapsed time + tokens after each response.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from glob import glob


def find_active_tracking():
    """
    Find the active tracking file.

    Returns the most recently started tracking that hasn't ended.
    Checks drafts first, then feature directories.
    """
    candidates = []

    # Check drafts
    for f in glob('docs/plans/_drafts/*/.tracking.json'):
        try:
            path = Path(f)
            tracking = json.loads(path.read_text())
            if tracking.get('plan') and not tracking['plan'].get('ended'):
                started = tracking['plan']['started']
                candidates.append((started, path, tracking))
        except (json.JSONDecodeError, FileNotFoundError):
            continue

    # Check feature plans
    for f in glob('docs/plans/*/.tracking.json'):
        if '_drafts' in f:
            continue
        try:
            path = Path(f)
            tracking = json.loads(path.read_text())

            # Check implement phase first (higher priority)
            if tracking.get('implement') and not tracking['implement'].get('ended'):
                started = tracking['implement']['started']
                candidates.append((started, path, tracking))
            # Then check plan phase
            elif tracking.get('plan') and not tracking['plan'].get('ended'):
                started = tracking['plan']['started']
                candidates.append((started, path, tracking))
        except (json.JSONDecodeError, FileNotFoundError):
            continue

    if not candidates:
        return None, None

    # Return most recently started
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def parse_transcript_tokens(transcript_path: str) -> tuple[int, int]:
    """
    Sum tokens from transcript JSONL file.

    Returns (tokens_in, tokens_out).
    """
    tokens_in = tokens_out = 0

    try:
        content = Path(transcript_path).read_text()
        for line in content.splitlines():
            if not line.strip():
                continue
            try:
                msg = json.loads(line)
                usage = msg.get('usage')
                if usage:
                    tokens_in += usage.get('input_tokens', 0)
                    tokens_out += usage.get('output_tokens', 0)
            except json.JSONDecodeError:
                continue
    except (FileNotFoundError, PermissionError):
        pass

    return tokens_in, tokens_out


def parse_iso(iso_str: str) -> datetime:
    """Parse ISO format timestamp to datetime."""
    # Handle both Z suffix and +00:00
    iso_str = iso_str.replace('Z', '+00:00')
    return datetime.fromisoformat(iso_str)


def format_duration(start_iso: str, end_iso: str = None) -> str:
    """Format duration between two timestamps."""
    start = parse_iso(start_iso)
    end = parse_iso(end_iso) if end_iso else datetime.now(timezone.utc)

    seconds = (end - start).total_seconds()
    minutes = int(seconds / 60)

    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
    elif minutes < 1:
        return "<1m"
    return f"{minutes}m"


def format_tokens(tokens_in: int, tokens_out: int) -> str:
    """Format token counts."""
    return f"{tokens_in:,} in / {tokens_out:,} out"


def build_display(tracking: dict) -> str:
    """Build the metrics display string."""
    lines = []

    feature_name = tracking.get('feature')
    if not feature_name:
        desc = tracking.get('description', 'unknown')
        feature_name = desc[:30] if desc else 'unknown'

    plan = tracking.get('plan')
    impl = tracking.get('implement')

    if impl and impl.get('started'):
        # Show both phases
        lines.append(f"⏱️  {feature_name}")

        if plan and plan.get('started'):
            duration = format_duration(plan['started'], plan.get('ended'))
            tokens = format_tokens(plan.get('tokens_in', 0), plan.get('tokens_out', 0))
            lines.append(f"    Planning:     {duration:>8} │ {tokens}")

        duration = format_duration(impl['started'], impl.get('ended'))
        tokens = format_tokens(impl.get('tokens_in', 0), impl.get('tokens_out', 0))
        lines.append(f"    Implementing: {duration:>8} │ {tokens}")

        # Total
        total_in = (plan.get('tokens_in', 0) if plan else 0) + impl.get('tokens_in', 0)
        total_out = (plan.get('tokens_out', 0) if plan else 0) + impl.get('tokens_out', 0)
        lines.append(f"    {'─' * 40}")
        lines.append(f"    Total: {format_tokens(total_in, total_out)}")

    elif plan and plan.get('started'):
        # Just planning phase
        duration = format_duration(plan['started'], plan.get('ended'))
        tokens = format_tokens(plan.get('tokens_in', 0), plan.get('tokens_out', 0))
        lines.append(f"⏱️  Planning: {duration} │ 📊 {tokens}")

    return "\n".join(lines)


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return

    # Skip if hook is already active (prevent infinite loops)
    if data.get('stop_hook_active'):
        print(json.dumps({"decision": "approve"}))
        return

    # Find active tracking
    tracking_file, tracking = find_active_tracking()
    if not tracking:
        print(json.dumps({"decision": "approve"}))
        return

    # Parse transcript for token counts
    transcript_path = data.get('transcript_path')
    if transcript_path:
        tokens_in, tokens_out = parse_transcript_tokens(transcript_path)

        # Update the active phase
        if tracking.get('implement') and not tracking['implement'].get('ended'):
            tracking['implement']['tokens_in'] = tokens_in
            tracking['implement']['tokens_out'] = tokens_out
        elif tracking.get('plan') and not tracking['plan'].get('ended'):
            tracking['plan']['tokens_in'] = tokens_in
            tracking['plan']['tokens_out'] = tokens_out

        # Save updated tracking
        try:
            tracking_file.write_text(json.dumps(tracking, indent=2))
        except (PermissionError, OSError):
            pass

    # Build and output display
    display = build_display(tracking)

    if display:
        print(json.dumps({
            "decision": "approve",
            "systemMessage": display
        }))
    else:
        print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
