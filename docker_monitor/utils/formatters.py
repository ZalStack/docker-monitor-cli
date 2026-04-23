"""Formatting utilities for display and calculations."""

import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

from docker_monitor.utils.constants import SIZE_UNITS, STATUS_COLORS


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    if size_bytes == 0:
        return "0 B"
    
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {SIZE_UNITS[i]}"


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a float as percentage string.
    
    Args:
        value: Float value (0-100)
        decimal_places: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    if value < 0:
        return "0.0%"
    return f"{value:.{decimal_places}f}%"


def format_uptime(started_at: str) -> str:
    """
    Calculate and format container uptime.
    
    Args:
        started_at: ISO format timestamp string
    
    Returns:
        Human readable uptime string
    """
    try:
        start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
        uptime = datetime.now(start_time.tzinfo) - start_time
        
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    except Exception:
        return "N/A"


def format_timestamp(timestamp: str) -> str:
    """
    Format Docker timestamp to readable date.
    
    Args:
        timestamp: Docker timestamp string
    
    Returns:
        Formatted date string
    """
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days > 365:
            return f"{diff.days // 365}y ago"
        elif diff.days > 30:
            return f"{diff.days // 30}mo ago"
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    except Exception:
        return "unknown"


def format_container_status(status: str) -> str:
    """
    Format container status for display.
    
    Args:
        status: Raw container status
    
    Returns:
        Formatted status string
    """
    status_map = {
        'running': '▶ Running',
        'exited': '⏹ Stopped',
        'paused': '⏸ Paused',
        'restarting': '↻ Restarting',
        'dead': '✗ Dead',
        'created': '● Created',
        'removing': '⌛ Removing'
    }
    
    return status_map.get(status.lower(), status)


def get_status_color(status: str) -> str:
    """
    Get color for container status.
    
    Args:
        status: Container status string
    
    Returns:
        Color name for rich formatting
    """
    return STATUS_COLORS.get(status.lower(), 'white')


def calculate_cpu_percent(stats: Dict[str, Any], 
                         previous_stats: Optional[Dict[str, Any]] = None) -> Tuple[float, float, float]:
    """
    Calculate CPU usage percentage for a container.
    
    Args:
        stats: Current container stats
        previous_stats: Previous stats for delta calculation
    
    Returns:
        Tuple of (cpu_delta, system_delta, cpu_percent)
    """
    cpu_stats = stats.get('cpu_stats', {})
    precpu_stats = stats.get('precpu_stats', {})
    
    cpu_usage = cpu_stats.get('cpu_usage', {})
    precpu_usage = precpu_stats.get('cpu_usage', {})
    
    cpu_delta = cpu_usage.get('total_usage', 0) - precpu_usage.get('total_usage', 0)
    system_delta = cpu_stats.get('system_cpu_usage', 0) - precpu_stats.get('system_cpu_usage', 0)
    
    if system_delta > 0 and cpu_delta > 0:
        online_cpus = cpu_stats.get('online_cpus', len(precpu_usage.get('percpu_usage', [1])))
        cpu_percent = (cpu_delta / system_delta) * online_cpus * 100
    else:
        cpu_percent = 0.0
    
    return cpu_delta, system_delta, cpu_percent


def format_network_rate(bytes_per_sec: float) -> str:
    """
    Format network transfer rate.
    
    Args:
        bytes_per_sec: Bytes per second
    
    Returns:
        Formatted rate string
    """
    return f"{format_size(int(bytes_per_sec))}/s"


def truncate_string(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Input string
        max_length: Maximum length
        suffix: Suffix to append when truncated
    
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix