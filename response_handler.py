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
    options: List[str]
) -> Dict[str, Any]:
    """
    Create success response JSON

    Args:
        vin: Processed VIN
        fnames: List of processed function names
        response_type: Response option used (1/2/3)
        options: List of option values used

    Returns:
        Success response dictionary
    """
    response = {
        "result": "success",
        "vin": vin,
        "fnames": fnames,
        "response_type": response_type,
        "options": options,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

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
            f"Options: {', '.join(response.get('options', []))}",
            f"Timestamp: {response.get('timestamp')}",
            "=" * 60
        ]
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
