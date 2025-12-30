#!/usr/bin/env python3
"""SessionStart hook: Load MEMORY.md and PLAN.md for in-progress features.

This hook runs when a Claude Code session starts and injects context
for any in-progress feature work, allowing seamless resume.

Usage in .claude/settings.json:
{
  "hooks": {
    "SessionStart": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "python3 intents-plugin/hooks/session_start.py"
      }]
    }]
  }
}
"""

import json
import sys
import os

# Add hooks directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hooks.utils.context import get_current_feature, load_context, format_context_message


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        # No input or invalid JSON - approve and continue
        print(json.dumps({"decision": "approve"}))
        return

    # Detect current in-progress feature
    feature = get_current_feature()

    if feature is None:
        # No in-progress feature, nothing to inject
        print(json.dumps({"decision": "approve"}))
        return

    # Load context files
    memory_content, plan_content = load_context(feature)

    if memory_content is None and plan_content is None:
        # Feature detected but no context files found
        print(json.dumps({"decision": "approve"}))
        return

    # Format and inject context as system message
    context_message = format_context_message(memory_content, plan_content, feature)

    print(json.dumps({
        "decision": "approve",
        "systemMessage": context_message
    }))


if __name__ == "__main__":
    main()
