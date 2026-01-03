"""ContextForge Feature Flags Module.

Simple feature flag system for toggling functionality at runtime.
Used for gradual rollout of new features and A/B testing.

Usage:
    from cf_core.feature_flags import is_enabled, set_flag

    set_flag("new_cli_output", True)
    if is_enabled("new_cli_output"):
        # Use new output format
        pass

Available flags:
    - No flags currently defined (add as needed)
"""

_flags: dict[str, bool] = {}


def is_enabled(flag: str) -> bool:
    """Check if a feature flag is enabled.

    Args:
        flag: The feature flag name to check.

    Returns:
        True if the flag is enabled, False otherwise (default).
    """
    return bool(_flags.get(flag, False))


def set_flag(flag: str, value: bool) -> None:
    """Set a feature flag value.

    Args:
        flag: The feature flag name to set.
        value: True to enable, False to disable.
    """
    _flags[flag] = bool(value)
