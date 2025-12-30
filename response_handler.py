"""
Response Handler Module
Generates success and error responses in JSON format
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from error_codes import ErrorCode, get_error_message
import logger


def create_success_response(
    vin: str,
    fnames: List[str],
    response_type: int,
    options: List[str],
    response_type2: Optional[int] = None
) -> Dict[str, Any]:
    """
    Create success response JSON

    Args:
        vin: Processed VIN
        fnames: List of processed function names
        response_type: Response option used (1/2/3)
        options: List of option values used
        response_type2: Optional response option for fname2 (1/2/3)

    Returns:
        Success response dictionary
    """
    response = {"result": "success"}
    response["vin"] = vin
    response["fnames"] = fnames
    response["response_type"] = response_type
    if response_type2 is not None:
        response["response_type2"] = response_type2
    response["options"] = options
    response["timestamp"] = datetime.utcnow().isoformat() + "Z"

    logger.log_info(f"Created success response for VIN: {vin}")
    return response


def create_error_response(
    error_code: ErrorCode,
    detail: str = ""
) -> Dict[str, Any]:
    """
    Create error response JSON

    Args:
        error_code: ErrorCode enum value
        detail: Optional additional detail for error message

    Returns:
        Error response dictionary
    """
    error_message = get_error_message(error_code, detail)

    response = {
        "result": "error",
        "error_code": error_code.value,
        "error_message": error_message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    logger.log_fail(f"Created error response: {error_code.value} - {error_message}")
    return response


def response_to_json(response: Dict[str, Any]) -> str:
    """
    Convert response dictionary to JSON string

    Args:
        response: Response dictionary

    Returns:
        JSON string
    """
    return json.dumps(response, indent=2)


def create_set_response(
    vin: str,
    fname: str,
    response_option: int,
    option: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create SET command success response

    Args:
        vin: VIN used
        fname: Function name processed
        response_option: Response option used
        option: Option value if response_option=2

    Returns:
        Success response dictionary
    """
    response = {
        "result": "success",
        "command": "SET",
        "vin": vin,
        "fname": fname,
        "response_option": response_option,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if response_option == 2 and option:
        response["option"] = option

    logger.log_info(f"Created SET response: fname={fname}")
    return response


def create_push_response(
    vin: str,
    topic: str,
    push_template: str
) -> Dict[str, Any]:
    """
    Create PUSH command success response

    Args:
        vin: VIN used
        topic: Push topic
        push_template: Push template name

    Returns:
        Success response dictionary
    """
    response = {
        "result": "success",
        "command": "PUSH",
        "vin": vin,
        "topic": topic,
        "push_template": push_template,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    logger.log_info(f"Created PUSH response: topic={topic}")
    return response


def create_close_response(vin: Optional[str] = None) -> Dict[str, Any]:
    """
    Create CLOSE command success response

    Args:
        vin: VIN that was in session (optional)

    Returns:
        Success response dictionary
    """
    response = {
        "result": "success",
        "command": "CLOSE",
        "message": "Session closed",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    if vin:
        response["vin"] = vin

    logger.log_info("Created CLOSE response")
    return response


def create_timeout_response(timeout_seconds: int) -> Dict[str, Any]:
    """
    Create session timeout response

    Args:
        timeout_seconds: Timeout value that was exceeded

    Returns:
        Timeout response dictionary
    """
    response = {
        "result": "timeout",
        "message": f"Session expired after {timeout_seconds} seconds",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    logger.log_info(f"Created timeout response: {timeout_seconds}s")
    return response


def format_response_for_display(response: Dict[str, Any]) -> str:
    """
    Format response for console display

    Args:
        response: Response dictionary

    Returns:
        Formatted string for display
    """
    if response.get('result') == 'success':
        lines = [
            "=" * 60,
            "SUCCESS",
            "=" * 60,
            f"VIN: {response.get('vin')}",
            f"Functions: {', '.join(response.get('fnames', []))}",
            f"Response Type: {response.get('response_type')}",
            f"Response Type 2: {response.get('response_type2')}"
            if response.get('response_type2') is not None else None,
            f"Options: {', '.join(response.get('options', []))}",
            f"Timestamp: {response.get('timestamp')}",
            "=" * 60
        ]
        lines = [line for line in lines if line is not None]
    else:
        lines = [
            "=" * 60,
            "ERROR",
            "=" * 60,
            f"Error Code: {response.get('error_code')}",
            f"Error Message: {response.get('error_message')}",
            f"Timestamp: {response.get('timestamp')}",
            "=" * 60
        ]

    return "\n".join(lines)
