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
    return slug[:50] if slug else 'unnamed'


def is_safe_path(name: str) -> bool:
    """Validate that a path component is safe (no traversal attacks)."""
    if not name:
        return False
    # Block path traversal attempts
    if '..' in name or name.startswith('/') or name.startswith('\\'):
        return False
    # Block absolute paths on Windows
    if len(name) > 1 and name[1] == ':':
        return False
    return True


def now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def handle_plan_command(description: str) -> None:
    """Initialize tracking for /intents:plan command."""
    slug = slugify(description)

    if not is_safe_path(slug):
        sys.stderr.write(f"[metrics] Invalid description for tracking: {description[:50]}\n")
        return

    tracking_dir = Path('docs/plans/_drafts') / slug
    tracking_file = tracking_dir / '.tracking.json'

    try:
        tracking_dir.mkdir(parents=True, exist_ok=True)

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
    except (PermissionError, OSError) as e:
        sys.stderr.write(f"[metrics] Failed to create tracking file: {e}\n")


def handle_implement_command(feature: str) -> None:
    """Initialize tracking for /intents:implement command."""
    # Strip quotes if present
    feature = feature.strip('"\'')

    if not is_safe_path(feature):
        sys.stderr.write(f"[metrics] Invalid feature name for tracking: {feature[:50]}\n")
        return

    tracking_file = Path('docs/plans') / feature / '.tracking.json'

    try:
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
    except (PermissionError, OSError, json.JSONDecodeError) as e:
        sys.stderr.write(f"[metrics] Failed to update tracking file: {e}\n")


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"decision": "approve"}))
        return

    prompt = data.get('prompt', '')

    # Detect /intents:plan <description> [--flags]
    # Captures description (quoted or unquoted) before any flags
    plan_match = re.match(
        r'/intents:plan\s+(?:"([^"]+)"|\'([^\']+)\'|(.+?))(?:\s+--.*|\s*$)',
        prompt,
        re.IGNORECASE
    )
    if plan_match:
        # Get whichever group matched (quoted double, quoted single, or unquoted)
        description = plan_match.group(1) or plan_match.group(2) or plan_match.group(3)
        if description:
            handle_plan_command(description.strip())

    # Detect /intents:implement <feature> [--flags]
    impl_match = re.match(
        r'/intents:implement\s+(?:"([^"]+)"|\'([^\']+)\'|(\S+))',
        prompt,
        re.IGNORECASE
    )
    if impl_match:
        feature = impl_match.group(1) or impl_match.group(2) or impl_match.group(3)
        if feature:
            handle_implement_command(feature.strip())

    # Always approve - this hook just initializes tracking
    print(json.dumps({"decision": "approve"}))


if __name__ == "__main__":
    main()
