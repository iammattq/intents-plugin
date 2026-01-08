#!/usr/bin/env python3
"""
UserPromptSubmit hook for intents-plugin token tracking.

Starts timers when /intents:plan or /intents:implement commands are invoked.
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime, timezone


def slugify(text: str) -> str:
    """Convert description to folder-safe slug."""
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug[:50]


def now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def handle_plan_command(description: str) -> None:
    """Initialize tracking for /intents:plan command."""
    slug = slugify(description)

    tracking_dir = Path(f'docs/plans/_drafts/{slug}')
    tracking_dir.mkdir(parents=True, exist_ok=True)
    tracking_file = tracking_dir / '.tracking.json'

    tracking = {
        "description": description,
        "feature": None,
        "plan": {
            "started": now_iso(),
            "ended": None,
            "tokens_in": 0,
            "tokens_out": 0
        },
        "implement": None
    }

    tracking_file.write_text(json.dumps(tracking, indent=2))


def handle_implement_command(feature: str) -> None:
    """Initialize tracking for /intents:implement command."""
    tracking_file = Path(f'docs/plans/{feature}/.tracking.json')

    if not tracking_file.exists():
        # No tracking file - create one for implement-only tracking
        tracking_file.parent.mkdir(parents=True, exist_ok=True)
        tracking = {
            "description": None,
            "feature": feature,
            "plan": None,
            "implement": {
                "started": now_iso(),
                "ended": None,
                "tokens_in": 0,
                "tokens_out": 0
            }
        }
    else:
        tracking = json.loads(tracking_file.read_text())

        # Mark plan as ended if not already
        if tracking.get('plan') and not tracking['plan'].get('ended'):
            tracking['plan']['ended'] = now_iso()

        # Start implement phase
        tracking['implement'] = {
            "started": now_iso(),
            "ended": None,
            "tokens_in": 0,
            "tokens_out": 0
        }

    tracking_file.write_text(json.dumps(tracking, indent=2))


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return

    prompt = data.get('prompt', '')

    # Detect /intents:plan <description>
    # Matches: /intents:plan "description" or /intents:plan description
    plan_match = re.match(r'/intents:plan\s+["\']?(.+?)["\']?\s*(?:--.*)?$', prompt, re.IGNORECASE)
    if plan_match:
        description = plan_match.group(1).strip()
        if description:
            handle_plan_command(description)

    # Detect /intents:implement <feature>
    impl_match = re.match(r'/intents:implement\s+(\S+)', prompt, re.IGNORECASE)
    if impl_match:
        feature = impl_match.group(1).strip()
        if feature:
            handle_implement_command(feature)

    # Always approve - this hook just initializes tracking
    print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
