#!/usr/bin/env python3
"""
Stop hook for intents-plugin token tracking.

Updates token counts and displays elapsed time + tokens after each response.
Calculates costs based on Claude model pricing.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from glob import glob


# Claude pricing per million tokens (as of Jan 2025)
# https://www.anthropic.com/pricing
PRICING = {
    'claude-sonnet-4': {
        'input': 3.00,
        'output': 15.00,
        'cache_read': 0.30,      # 90% discount on cached input
        'cache_create': 3.75,    # 25% premium for cache creation
    },
    'claude-opus-4': {
        'input': 15.00,
        'output': 75.00,
        'cache_read': 1.50,
        'cache_create': 18.75,
    },
    'claude-haiku-3.5': {
        'input': 0.80,
        'output': 4.00,
        'cache_read': 0.08,
        'cache_create': 1.00,
    },
    # Default fallback (Sonnet pricing)
    'default': {
        'input': 3.00,
        'output': 15.00,
        'cache_read': 0.30,
        'cache_create': 3.75,
    },
}


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


def parse_transcript_tokens(transcript_path: str) -> dict:
    """
    Sum tokens from transcript JSONL file.

    Returns dict with token counts by type:
    {
        'input_tokens': int,
        'output_tokens': int,
        'cache_read_tokens': int,
        'cache_creation_tokens': int,
        'model': str  # Most recently used model
    }
    """
    totals = {
        'input_tokens': 0,
        'output_tokens': 0,
        'cache_read_tokens': 0,
        'cache_creation_tokens': 0,
        'model': 'default',
    }

    try:
        content = Path(transcript_path).read_text()
        for line in content.splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)

                # Usage can be in multiple locations depending on message type
                usage = None

                # Check nested message.usage (most common for assistant messages)
                if isinstance(entry.get('message'), dict):
                    usage = entry['message'].get('usage')
                    # Also try to get model from message
                    if entry['message'].get('model'):
                        totals['model'] = entry['message']['model']

                # Fallback: check root level (some message types)
                if not usage:
                    usage = entry.get('usage')

                # Check for model at root level
                if entry.get('model'):
                    totals['model'] = entry['model']

                if usage:
                    # Standard input/output tokens
                    totals['input_tokens'] += usage.get('input_tokens', 0)
                    totals['output_tokens'] += usage.get('output_tokens', 0)

                    # Cache tokens (important for accurate cost calculation)
                    totals['cache_read_tokens'] += usage.get('cache_read_input_tokens', 0)
                    totals['cache_creation_tokens'] += usage.get('cache_creation_input_tokens', 0)

            except json.JSONDecodeError:
                continue
    except (FileNotFoundError, PermissionError):
        pass

    return totals


def calculate_cost(tokens: dict) -> float:
    """
    Calculate cost in USD based on token counts and model.

    Args:
        tokens: Dict with input_tokens, output_tokens, cache_read_tokens,
                cache_creation_tokens, and model

    Returns:
        Cost in USD
    """
    model = tokens.get('model', 'default')

    # Find matching pricing (check for partial model name matches)
    pricing = PRICING['default']
    for model_key, model_pricing in PRICING.items():
        if model_key in model.lower():
            pricing = model_pricing
            break

    # Calculate cost per million tokens
    cost = 0.0
    cost += (tokens.get('input_tokens', 0) / 1_000_000) * pricing['input']
    cost += (tokens.get('output_tokens', 0) / 1_000_000) * pricing['output']
    cost += (tokens.get('cache_read_tokens', 0) / 1_000_000) * pricing['cache_read']
    cost += (tokens.get('cache_creation_tokens', 0) / 1_000_000) * pricing['cache_create']

    return cost


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


def format_tokens(tokens_in: int, tokens_out: int, cost: float = None) -> str:
    """Format token counts with optional cost."""
    token_str = f"{tokens_in:,} in / {tokens_out:,} out"
    if cost is not None:
        return f"{token_str} │ ${cost:.2f}"
    return token_str


def get_total_input_tokens(phase: dict) -> int:
    """Get total input tokens including cache tokens."""
    return (
        phase.get('tokens_in', 0) +
        phase.get('cache_read_tokens', 0) +
        phase.get('cache_creation_tokens', 0)
    )


def calculate_phase_cost(phase: dict) -> float:
    """Calculate cost for a single phase."""
    if not phase:
        return 0.0
    return calculate_cost({
        'input_tokens': phase.get('tokens_in', 0),
        'output_tokens': phase.get('tokens_out', 0),
        'cache_read_tokens': phase.get('cache_read_tokens', 0),
        'cache_creation_tokens': phase.get('cache_creation_tokens', 0),
        'model': phase.get('model', 'default'),
    })


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
            plan_in = get_total_input_tokens(plan)
            plan_cost = calculate_phase_cost(plan)
            tokens = format_tokens(plan_in, plan.get('tokens_out', 0), plan_cost)
            lines.append(f"    Planning:     {duration:>8} │ {tokens}")

        duration = format_duration(impl['started'], impl.get('ended'))
        impl_in = get_total_input_tokens(impl)
        impl_cost = calculate_phase_cost(impl)
        tokens = format_tokens(impl_in, impl.get('tokens_out', 0), impl_cost)
        lines.append(f"    Implementing: {duration:>8} │ {tokens}")

        # Total
        total_in = (get_total_input_tokens(plan) if plan else 0) + get_total_input_tokens(impl)
        total_out = (plan.get('tokens_out', 0) if plan else 0) + impl.get('tokens_out', 0)
        total_cost = (calculate_phase_cost(plan) if plan else 0) + calculate_phase_cost(impl)
        lines.append(f"    {'─' * 48}")
        lines.append(f"    Total: {format_tokens(total_in, total_out, total_cost)}")

    elif plan and plan.get('started'):
        # Just planning phase
        duration = format_duration(plan['started'], plan.get('ended'))
        plan_in = get_total_input_tokens(plan)
        plan_cost = calculate_phase_cost(plan)
        tokens = format_tokens(plan_in, plan.get('tokens_out', 0), plan_cost)
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
        tokens = parse_transcript_tokens(transcript_path)

        # Update the active phase with all token types
        def update_phase(phase: dict):
            phase['tokens_in'] = tokens['input_tokens']
            phase['tokens_out'] = tokens['output_tokens']
            phase['cache_read_tokens'] = tokens['cache_read_tokens']
            phase['cache_creation_tokens'] = tokens['cache_creation_tokens']
            phase['model'] = tokens['model']

        if tracking.get('implement') and not tracking['implement'].get('ended'):
            update_phase(tracking['implement'])
        elif tracking.get('plan') and not tracking['plan'].get('ended'):
            update_phase(tracking['plan'])

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
