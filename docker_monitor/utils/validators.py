"""Validation utilities for input parameters."""

import re
from typing import Union


def validate_container_name(name: str) -> bool:
    """
    Validate container name format.
    
    Args:
        name: Container name to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not name or len(name) > 255:
        return False
    
    # Container name pattern (alphanumeric, underscore, dot, hyphen)
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_.-]+$'
    return bool(re.match(pattern, name))


def validate_timeout(timeout: Union[int, float]) -> bool:
    """
    Validate timeout value.
    
    Args:
        timeout: Timeout in seconds
    
    Returns:
        True if valid
    """
    try:
        timeout_float = float(timeout)
        return timeout_float > 0 and timeout_float <= 3600  # Max 1 hour
    except (TypeError, ValueError):
        return False


def validate_interval(interval: Union[int, float]) -> bool:
    """
    Validate refresh interval.
    
    Args:
        interval: Interval in seconds
    
    Returns:
        True if valid
    """
    try:
        interval_float = float(interval)
        return interval_float >= 0.5 and interval_float <= 60  # Min 0.5s, max 60s
    except (TypeError, ValueError):
        return False


def validate_port(port: Union[int, str]) -> bool:
    """
    Validate port number.
    
    Args:
        port: Port number
    
    Returns:
        True if valid
    """
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (TypeError, ValueError):
        return False