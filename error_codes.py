"""
Error codes and messages for TCP-Controlled Web Browser Automation Module
"""

from enum import Enum


class ErrorCode(Enum):
    """Error codes for automation module"""
    TCP_CONNECTION_ERROR = 1001
    LOGIN_FAILURE = 1002
    INVALID_COMMAND_FORMAT = 1003
    MISSING_REQUIRED_PARAMS = 1004
    VIN_NOT_FOUND = 1005
    FUNCTION_NAME_NOT_FOUND = 1006
    INVALID_RESPONSE_OPTION = 1007
    ELEMENT_WAIT_TIMEOUT = 1008
    JSON_PARSING_ERROR = 1009
    BROWSER_CRASH = 1010
    UNKNOWN_ERROR = 1011
    PUSH_COMMAND_FAILED = 1012
    SESSION_TIMEOUT = 1013
    NO_ACTIVE_SESSION = 1014


# Error message mapping
ERROR_MESSAGES = {
    ErrorCode.TCP_CONNECTION_ERROR: "TCP connection error",
    ErrorCode.LOGIN_FAILURE: "Login failure after maximum retries",
    ErrorCode.INVALID_COMMAND_FORMAT: "Invalid command format",
    ErrorCode.MISSING_REQUIRED_PARAMS: "Missing required parameters",
    ErrorCode.VIN_NOT_FOUND: "VIN not found in search results",
    ErrorCode.FUNCTION_NAME_NOT_FOUND: "Function name not found in table",
    ErrorCode.INVALID_RESPONSE_OPTION: "Invalid response_option value (must be 1, 2, or 3)",
    ErrorCode.ELEMENT_WAIT_TIMEOUT: "Timeout waiting for web element",
    ErrorCode.JSON_PARSING_ERROR: "JSON parsing or modification error",
    ErrorCode.BROWSER_CRASH: "Browser crashed during operation",
    ErrorCode.UNKNOWN_ERROR: "Unknown error occurred",
    ErrorCode.PUSH_COMMAND_FAILED: "Push command failed",
    ErrorCode.SESSION_TIMEOUT: "Session timeout",
    ErrorCode.NO_ACTIVE_SESSION: "No active session"
}


def get_error_message(error_code: ErrorCode, detail: str = "") -> str:
    """
    Get error message for given error code with optional detail

    Args:
        error_code: ErrorCode enum value
        detail: Optional additional detail to append to message

    Returns:
        Formatted error message string
    """
    base_message = ERROR_MESSAGES.get(error_code, "Unknown error")
    if detail:
        return f"{base_message}: {detail}"
    return base_message
