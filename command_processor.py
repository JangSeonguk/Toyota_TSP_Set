"""
Command Processor Module
Validates commands and manages command queue
"""

import queue
import json
from typing import Dict, Any, Optional, Tuple

from error_codes import ErrorCode
import logger


class CommandQueue:
    """Thread-safe FIFO command queue"""

    def __init__(self):
        self._queue = queue.Queue()
        logger.log_info("Command queue initialized")

    def enqueue(self, command: Dict[str, Any]):
        """
        Add command to queue

        Args:
            command: Command dictionary
        """
        self._queue.put(command)
        size = self._queue.qsize()
        logger.log_info(f"Command enqueued (queue size: {size})")

    def dequeue(self, block: bool = True, timeout: Optional[float] = None) -> Dict[str, Any]:
        """
        Remove and return command from queue (FIFO)

        Args:
            block: Block if queue is empty (default: True)
            timeout: Timeout for blocking (default: None)

        Returns:
            Command dictionary

        Raises:
            queue.Empty: If queue is empty and block=False or timeout expires
        """
        command = self._queue.get(block=block, timeout=timeout)
        size = self._queue.qsize()
        logger.log_info(f"Command dequeued (queue size: {size})")
        return command

    def size(self) -> int:
        """
        Get current queue size

        Returns:
            Number of commands in queue
        """
        return self._queue.qsize()

    def is_empty(self) -> bool:
        """
        Check if queue is empty

        Returns:
            True if empty, False otherwise
        """
        return self._queue.empty()


def validate_command(command_dict: Dict[str, Any]) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
    """
    Validate command structure and parameters

    Args:
        command_dict: Command dictionary

    Returns:
        Tuple of (is_valid: bool, error_code or None, error_detail or None)
    """
    # Check command type
    command_type = command_dict.get('command')

    if not command_type:
        return False, ErrorCode.INVALID_COMMAND_FORMAT, "Missing 'command' field"

    valid_commands = ['START', 'STOP', 'SET', 'PUSH', 'CLOSE']
    if command_type not in valid_commands:
        return False, ErrorCode.INVALID_COMMAND_FORMAT, f"Invalid command type: {command_type}"

    # STOP command requires no additional validation
    if command_type == 'STOP':
        logger.log_info("STOP command validated")
        return True, None, None

    # CLOSE command requires no additional validation
    if command_type == 'CLOSE':
        logger.log_info("CLOSE command validated")
        return True, None, None

    # SET command validation
    if command_type == 'SET':
        return _validate_set_command(command_dict)

    # PUSH command validation
    if command_type == 'PUSH':
        return _validate_push_command(command_dict)

    # Validate START command parameters
    required_params = ['id', 'password', 'vin', 'fname1', 'response_option']

    for param in required_params:
        if param not in command_dict or command_dict[param] is None:
            return False, ErrorCode.MISSING_REQUIRED_PARAMS, f"Missing required parameter: {param}"

    # Validate response_option value
    response_option = command_dict.get('response_option')
    if response_option not in [1, 2, 3]:
        return False, ErrorCode.INVALID_RESPONSE_OPTION, f"response_option must be 1, 2, or 3, got: {response_option}"

    # Validate option1 usage
    if response_option == 2:
        if not command_dict.get('option1'):
            return False, ErrorCode.MISSING_REQUIRED_PARAMS, "option1 required when response_option is 2"
    else:
        # Ignore option1 for response_option 1 or 3
        command_dict['option1'] = None

    # Validate fname2 and response_option2/option2 consistency
    fname2 = command_dict.get('fname2')
    option2 = command_dict.get('option2')
    response_option2 = command_dict.get('response_option2')

    if fname2:
        if response_option2 is None:
            # Backward-compatible default when response_option2 is omitted
            response_option2 = response_option
            command_dict['response_option2'] = response_option2

        if response_option2 not in [1, 2, 3]:
            return False, ErrorCode.INVALID_RESPONSE_OPTION, (
                f"response_option2 must be 1, 2, or 3, got: {response_option2}"
            )

        if response_option2 == 2:
            if not option2:
                return False, ErrorCode.MISSING_REQUIRED_PARAMS, (
                    "option2 required when fname2 is provided and response_option2 is 2"
                )
        else:
            # Ignore option2 for response_option2 1 or 3
            command_dict['option2'] = None
    else:
        command_dict['response_option2'] = None
        command_dict['option2'] = None

    # Validate add_request option (optional, defaults to False)
    add_request = command_dict.get('add_request', False)
    if not isinstance(add_request, bool):
        return False, ErrorCode.INVALID_COMMAND_FORMAT, "add_request must be a boolean"

    # Note: timeout parameter is ignored (no session timeout)

    logger.log_info(f"START command validated: VIN={command_dict.get('vin')}, fname1={command_dict.get('fname1')}, add_request={add_request}")
    return True, None, None


def _validate_set_command(command_dict: Dict[str, Any]) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
    """
    Validate SET command parameters

    Args:
        command_dict: Command dictionary

    Returns:
        Tuple of (is_valid: bool, error_code or None, error_detail or None)
    """
    # Required parameters for SET command
    fname = command_dict.get('fname')
    if not fname:
        return False, ErrorCode.MISSING_REQUIRED_PARAMS, "Missing required parameter: fname"

    response_option = command_dict.get('response_option')
    if response_option is None:
        return False, ErrorCode.MISSING_REQUIRED_PARAMS, "Missing required parameter: response_option"

    if response_option not in [1, 2, 3]:
        return False, ErrorCode.INVALID_RESPONSE_OPTION, f"response_option must be 1, 2, or 3, got: {response_option}"

    # option is required when response_option is 2
    if response_option == 2:
        option = command_dict.get('option')
        if not option:
            return False, ErrorCode.MISSING_REQUIRED_PARAMS, "option required when response_option is 2"

    logger.log_info(f"SET command validated: fname={fname}, response_option={response_option}")
    return True, None, None


def _validate_push_command(command_dict: Dict[str, Any]) -> Tuple[bool, Optional[ErrorCode], Optional[str]]:
    """
    Validate PUSH command parameters

    Args:
        command_dict: Command dictionary

    Returns:
        Tuple of (is_valid: bool, error_code or None, error_detail or None)
    """
    # Required parameters for PUSH command
    topic = command_dict.get('topic')
    if not topic:
        return False, ErrorCode.MISSING_REQUIRED_PARAMS, "Missing required parameter: topic"

    push_template = command_dict.get('push_template')
    if not push_template:
        return False, ErrorCode.MISSING_REQUIRED_PARAMS, "Missing required parameter: push_template"

    logger.log_info(f"PUSH command validated: topic={topic}, push_template={push_template}")
    return True, None, None


def parse_command_json(json_string: str) -> Tuple[Optional[Dict[str, Any]], Optional[ErrorCode], Optional[str]]:
    """
    Parse JSON string to command dictionary

    Args:
        json_string: JSON string

    Returns:
        Tuple of (command_dict or None, error_code or None, error_detail or None)
    """
    try:
        command_dict = json.loads(json_string)
        logger.log_info("Command JSON parsed successfully")
        return command_dict, None, None
    except json.JSONDecodeError as e:
        logger.log_fail(f"Failed to parse command JSON: {e}")
        return None, ErrorCode.INVALID_COMMAND_FORMAT, f"JSON parse error: {str(e)}"
    except Exception as e:
        logger.log_error("Unexpected error parsing command JSON", e)
        return None, ErrorCode.UNKNOWN_ERROR, f"Parse error: {str(e)}"
