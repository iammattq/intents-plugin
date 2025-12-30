"""Hook utilities for intents-plugin."""

from .context import (
    load_context,
    find_memory_file,
    find_plan_file,
    get_current_feature,
    _validate_feature_name,
)
from .checks import (
    get_test_command,
    run_checks,
    format_block_reason,
    get_retry_count,
    increment_retry_count,
    reset_retry_count,
    check_retry_limit,
    MAX_RETRIES,
)
from .memory import update_chunk_status, add_session_log_entry, get_current_phase
from .plan_verify import verify_implementation, format_verification_failures
from .graph import update_graph_status, is_feature_complete, get_feature_status

__all__ = [
    # Context
    'load_context',
    'find_memory_file',
    'find_plan_file',
    'get_current_feature',
    '_validate_feature_name',
    # Checks
    'get_test_command',
    'run_checks',
    'format_block_reason',
    'get_retry_count',
    'increment_retry_count',
    'reset_retry_count',
    'check_retry_limit',
    'MAX_RETRIES',
    # Memory
    'update_chunk_status',
    'add_session_log_entry',
    'get_current_phase',
    # Plan verification
    'verify_implementation',
    'format_verification_failures',
    # Graph
    'update_graph_status',
    'is_feature_complete',
    'get_feature_status',
]
