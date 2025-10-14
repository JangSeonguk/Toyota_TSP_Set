"""
Logger module for TCP-Controlled Web Browser Automation Module
Console-only logging with INFO, SUCCESS, and FAIL prefixes
"""

import sys
import time
from datetime import datetime
from typing import Optional


# Global flag to control debug output
_debug_enabled = False


def enable_debug():
    """Enable debug logging output"""
    global _debug_enabled
    _debug_enabled = True


def disable_debug():
    """Disable debug logging output"""
    global _debug_enabled
    _debug_enabled = False


def is_debug_enabled() -> bool:
    """Check if debug logging is enabled"""
    return _debug_enabled


def _log(prefix: str, message: str, file=sys.stdout):
    """
    Internal logging function with timestamp

    Args:
        prefix: Log level prefix (INFO, SUCCESS, FAIL)
        message: Log message
        file: Output file stream (default: stdout)
    """
    if not _debug_enabled:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] [{prefix}] {message}"
    print(log_line, file=file, flush=True)


def log_info(message: str):
    """
    Log informational message with [INFO] prefix

    Args:
        message: Message to log
    """
    _log("INFO", message)


def log_success(message: str):
    """
    Log success message with [SUCCESS] prefix

    Args:
        message: Message to log
    """
    _log("SUCCESS", message)


def log_fail(message: str):
    """
    Log failure message with [FAIL] prefix

    Args:
        message: Message to log
    """
    _log("FAIL", message, file=sys.stderr)


def log_error(message: str, exception: Optional[Exception] = None):
    """
    Log error message with [FAIL] prefix and optional exception details

    Args:
        message: Error message to log
        exception: Optional exception object to include details
    """
    if exception:
        _log("FAIL", f"{message} - {type(exception).__name__}: {str(exception)}", file=sys.stderr)
    else:
        _log("FAIL", message, file=sys.stderr)


def debug_sleep(interval: float = 2.0, reason: str = "Debug interval"):
    """
    Sleep for specified interval when DEBUG_MODE is enabled

    Args:
        interval: Number of seconds to sleep
        reason: Reason for the sleep (for logging)
    """
    import config

    if config.DEBUG_MODE:
        log_info(f"{reason} - waiting {interval}s...")
        time.sleep(interval)
