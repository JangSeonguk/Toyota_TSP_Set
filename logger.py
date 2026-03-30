"""
Logger module for TCP-Controlled Web Browser Automation Module
Console and file logging with INFO, SUCCESS, and FAIL prefixes

When TSP_AUTO_DEBUG environment variable is set to '1' (via runtime_hook_debug.py),
debug logging is automatically enabled and logs are written to a file
in the same directory as the executable.
"""

import os
import sys
import time
from datetime import datetime
from typing import Optional


# Global flag to control debug output
_debug_enabled = False

# File logging (enabled by TSP_AUTO_DEBUG env var or debug build)
_log_file_path = None
_log_file = None


def _get_log_dir():
    """Get the directory for log and diagnostic files (exe directory)"""
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_log_dir():
    """Public accessor for log directory path"""
    return _get_log_dir()


def _init_file_logging():
    """Initialize file logging to exe directory"""
    global _log_file_path, _log_file
    if _log_file is not None:
        return

    try:
        exe_dir = _get_log_dir()
        _log_file_path = os.path.join(exe_dir, "tsp_auto_debug.log")
        _log_file = open(_log_file_path, 'a', encoding='utf-8')
    except Exception:
        _log_file = None


# Auto-enable debug if TSP_AUTO_DEBUG env var is set (debug build)
if os.environ.get('TSP_AUTO_DEBUG') == '1':
    _debug_enabled = True
    _init_file_logging()


def enable_debug():
    """Enable debug logging output and file logging"""
    global _debug_enabled
    _debug_enabled = True
    _init_file_logging()


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

    # Write to log file if file logging is active
    if _log_file is not None:
        try:
            _log_file.write(log_line + '\n')
            _log_file.flush()
        except Exception:
            pass


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
