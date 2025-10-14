"""
Automation Workflow Module
Implements the 8-step web automation workflow
"""

import json
from typing import Optional, Tuple, List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import config
import logger
from error_codes import ErrorCode, get_error_message
import browser_manager


def search_vin(vin: str) -> Tuple[bool, Optional[ErrorCode]]:
    """
    Search for VIN and click first result

    Args:
        vin: VIN search term

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    logger.log_info(f"Searching for VIN: {vin}")

    browser = browser_manager.get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, ErrorCode.BROWSER_CRASH

    try:
        # Wait for VIN input field
        success, vin_input, error = browser_manager.wait_for_element(
            config.SELECTORS['vin_input']
        )
        if not success:
            return False, error

        # Enter VIN
        logger.log_info(f"Entering VIN: {vin}")
        vin_input.clear()
        vin_input.send_keys(vin)
        vin_input.send_keys(Keys.RETURN)

        # Wait for first result row to be clickable
        logger.log_info("Waiting for first VIN result to be clickable")
        logger.debug_sleep(config.DEBUG_INTERVAL, "After VIN search")

        success, result_row, error = browser_manager.wait_for_clickable(
            config.SELECTORS['vin_result_row']
        )
        if not success:
            logger.log_fail(f"VIN result not clickable: {vin}")
            return False, error

        # Click first result
        logger.log_info("Clicking first VIN result")
        result_row.click()

        logger.log_success(f"VIN search successful: {vin}")
        return True, None

    except Exception as e:
        logger.log_error(f"Error searching for VIN: {vin}", e)
        return False, ErrorCode.UNKNOWN_ERROR


def search_function_name(fname: str) -> Tuple[bool, Optional[ErrorCode]]:
    """
    Search for function name in table and click matching row

    Args:
        fname: Function name to search for

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    logger.log_info(f"Searching for function name: {fname}")

    browser = browser_manager.get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, ErrorCode.BROWSER_CRASH

    try:
        # Wait for table to load by checking for at least one function name cell
        import time
        max_wait = config.ELEMENT_WAIT_TIMEOUT
        wait_interval = 0.5
        elapsed = 0

        cells = []
        while elapsed < max_wait:
            cells = browser.find_elements(By.CSS_SELECTOR, config.SELECTORS['function_name_cell'])
            if cells:
                break
            time.sleep(wait_interval)
            elapsed += wait_interval

        # Get all function name cells (column 3)
        cells = browser.find_elements(By.CSS_SELECTOR, config.SELECTORS['function_name_cell'])

        if not cells:
            logger.log_fail(f"No function name cells found")
            return False, ErrorCode.FUNCTION_NAME_NOT_FOUND

        logger.log_info(f"Found {len(cells)} function name cells")

        # Find matching cell
        for cell in cells:
            cell_text = cell.text.strip()
            if cell_text == fname:
                logger.log_info(f"Found matching function name: {fname}")
                logger.debug_sleep(config.DEBUG_INTERVAL, "After finding function name")

                # Click the parent row
                try:
                    # Get the parent tr element
                    row = cell.find_element(By.XPATH, './ancestor::tr')

                    # Wait a moment for row to be ready
                    import time
                    time.sleep(0.3)

                    # Try multiple click methods for robustness
                    try:
                        # Method 1: Direct click
                        row.click()
                        logger.log_success(f"Clicked function name row: {fname}")
                        return True, None
                    except Exception as direct_error:
                        logger.log_info(f"Direct click failed, trying JavaScript click: {direct_error}")
                        # Method 2: JavaScript click
                        browser.execute_script("arguments[0].click();", row)
                        logger.log_success(f"Clicked function name row via JavaScript: {fname}")
                        return True, None

                except Exception as e:
                    logger.log_error(f"Error clicking function name row", e)
                    return False, ErrorCode.UNKNOWN_ERROR

        # No match found
        logger.log_fail(f"Function name not found: {fname}")
        return False, ErrorCode.FUNCTION_NAME_NOT_FOUND

    except Exception as e:
        logger.log_error(f"Error searching for function name: {fname}", e)
        return False, ErrorCode.UNKNOWN_ERROR


def select_response_option(option: int) -> Tuple[bool, Optional[ErrorCode]]:
    """
    Select radio button corresponding to response option

    Args:
        option: Response option (1=default, 2=custom, 3=no_response)

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    logger.log_info(f"Selecting response option: {option}")

    if option not in [1, 2, 3]:
        logger.log_fail(f"Invalid response option: {option}")
        return False, ErrorCode.INVALID_RESPONSE_OPTION

    browser = browser_manager.get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, ErrorCode.BROWSER_CRASH

    try:
        # Map option to radio button ID
        radio_id_map = {
            1: config.SELECTORS['radio_default'],
            2: config.SELECTORS['radio_custom'],
            3: config.SELECTORS['radio_no_response']
        }

        radio_id = radio_id_map[option]
        logger.log_info(f"Looking for radio button: {radio_id}")
        logger.debug_sleep(config.DEBUG_INTERVAL, "Before selecting radio button")

        # Method 1: Try clicking the label element (most reliable for radio buttons)
        try:
            label_selector = f'label[for="{radio_id}"]'

            # Wait for label to be clickable
            success, label_element, error = browser_manager.wait_for_clickable(
                label_selector
            )
            if success:
                label_element.click()
                logger.log_success(f"Response option {option} selected (clicked label)")
                return True, None
            else:
                logger.log_info(f"Label not clickable, trying radio button directly")
        except Exception as label_error:
            logger.log_info(f"Label click failed: {label_error}")

        # Method 2: Try waiting for radio button to be clickable
        try:
            success, radio_button, error = browser_manager.wait_for_clickable(
                radio_id,
                by=By.ID
            )
            if not success:
                logger.log_fail(f"Radio button not clickable: {radio_id}")
                return False, error

            # Try JavaScript click on the input element (more reliable than direct click)
            browser.execute_script("arguments[0].click();", radio_button)
            logger.log_success(f"Response option {option} selected (JavaScript click)")
            return True, None
        except Exception as js_error:
            logger.log_info(f"JavaScript click failed: {js_error}")

            # Method 3: Try direct click as last resort
            try:
                radio_button.click()
                logger.log_success(f"Response option {option} selected (direct click)")
                return True, None
            except Exception as direct_error:
                logger.log_fail(f"All click methods failed")
                raise direct_error

    except Exception as e:
        logger.log_error(f"Error selecting response option: {option}", e)
        return False, ErrorCode.UNKNOWN_ERROR


def modify_json_type(option_value: str) -> Tuple[bool, Optional[ErrorCode]]:
    """
    Modify JSON header.message.type value in textarea

    Args:
        option_value: New value for header.message.type

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    logger.log_info(f"Modifying JSON type to: {option_value}")

    browser = browser_manager.get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, ErrorCode.BROWSER_CRASH

    try:
        # Wait for JSON textarea
        success, textarea, error = browser_manager.wait_for_element(
            config.SELECTORS['json_textarea']
        )
        if not success:
            logger.log_fail("JSON textarea not found")
            return False, error

        # Get current JSON text
        json_text = textarea.get_attribute('value')
        logger.log_info(f"Current JSON length: {len(json_text)} characters")

        # Parse JSON
        try:
            json_data = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.log_fail(f"Failed to parse JSON: {e}")
            return False, ErrorCode.JSON_PARSING_ERROR

        # Navigate to header.message.type and modify
        try:
            if 'header' not in json_data:
                json_data['header'] = {}
            if 'message' not in json_data['header']:
                json_data['header']['message'] = {}

            json_data['header']['message']['type'] = option_value
            logger.log_info(f"Modified JSON: header.message.type = {option_value}")

        except Exception as e:
            logger.log_fail(f"Failed to navigate JSON structure: {e}")
            return False, ErrorCode.JSON_PARSING_ERROR

        # Convert back to JSON string (compact format, no indent to match original)
        try:
            modified_json = json.dumps(json_data, separators=(',', ':'))
        except Exception as e:
            logger.log_fail(f"Failed to serialize JSON: {e}")
            return False, ErrorCode.JSON_PARSING_ERROR

        # Log the modified JSON for verification (pretty-printed for readability)
        logger.log_info("Modified JSON content (formatted for readability):")
        logger.log_info("=" * 60)
        try:
            pretty_json = json.dumps(json_data, indent=2)
            for line in pretty_json.split('\n'):
                logger.log_info(line)
        except:
            logger.log_info(modified_json)
        logger.log_info("=" * 60)

        # Set textarea value using JavaScript and trigger events
        logger.debug_sleep(config.DEBUG_INTERVAL, "Before modifying JSON")
        browser.execute_script("""
            arguments[0].value = arguments[1];
            // Trigger input event for Vue.js/React to detect change
            var event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
            // Also trigger change event for compatibility
            var changeEvent = new Event('change', { bubbles: true });
            arguments[0].dispatchEvent(changeEvent);
        """, textarea, modified_json)

        logger.log_success("JSON modified successfully")
        return True, None

    except Exception as e:
        logger.log_error("Error modifying JSON", e)
        return False, ErrorCode.UNKNOWN_ERROR


def click_update_button() -> Tuple[bool, Optional[ErrorCode]]:
    """
    Click the Update button

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    logger.log_info("Clicking Update button")

    browser = browser_manager.get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, ErrorCode.BROWSER_CRASH

    try:
        # Wait for update button to be clickable
        logger.debug_sleep(config.DEBUG_INTERVAL, "Before clicking update button")

        success, update_btn, error = browser_manager.wait_for_clickable(
            config.SELECTORS['update_button']
        )
        if not success:
            logger.log_fail("Update button not clickable")
            return False, error

        # Verify button text contains "Update"
        button_text = update_btn.text.strip()
        logger.log_info(f"Found button with text: '{button_text}'")

        if "Update" not in button_text:
            logger.log_fail(f"Button text does not contain 'Update': {button_text}")
            return False, ErrorCode.UNKNOWN_ERROR

        # Try multiple click methods for robustness
        try:
            # Method 1: Direct click
            update_btn.click()
            logger.log_success("Update button clicked (direct click)")
        except Exception as direct_error:
            logger.log_info(f"Direct click failed: {direct_error}")
            try:
                # Method 2: JavaScript click
                browser.execute_script("arguments[0].click();", update_btn)
                logger.log_success("Update button clicked (JavaScript click)")
            except Exception as js_error:
                logger.log_fail(f"All click methods failed: {js_error}")
                return False, ErrorCode.UNKNOWN_ERROR

        # Wait longer for page transition to ensure update is processed
        import time
        time.sleep(1.0)

        logger.log_success("Update completed")
        return True, None

    except Exception as e:
        logger.log_error("Error clicking update button", e)
        return False, ErrorCode.UNKNOWN_ERROR


def process_function_name(
    fname: str,
    response_option: int,
    option_value: Optional[str]
) -> Tuple[bool, Optional[ErrorCode]]:
    """
    Process a single function name (steps 4-7):
    - Search function name
    - Select response option
    - Modify JSON (if option 2)
    - Click update button

    Args:
        fname: Function name to process
        response_option: Response option (1/2/3)
        option_value: Value for JSON modification (required if option 2)

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    logger.log_info(f"Processing function name: {fname}, option: {response_option}")

    # Step 4: Search function name
    success, error = search_function_name(fname)
    if not success:
        return False, error

    # Small delay for page stabilization after function name click
    import time
    time.sleep(0.5)

    # Step 5: Select response option
    success, error = select_response_option(response_option)
    if not success:
        return False, error

    # Step 6: Modify JSON if option is 2 (custom)
    if response_option == 2:
        if not option_value:
            logger.log_fail("option_value required for response_option 2")
            return False, ErrorCode.MISSING_REQUIRED_PARAMS

        success, error = modify_json_type(option_value)
        if not success:
            return False, error

    # Step 7: Click update button
    success, error = click_update_button()
    if not success:
        return False, error

    logger.log_success(f"Function name processed successfully: {fname}")
    return True, None


def execute_automation(command_data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, Any]], Optional[ErrorCode]]:
    """
    Execute full automation workflow

    Args:
        command_data: Command dictionary with keys:
            - id: Login username
            - password: Login password
            - vin: VIN to search
            - fname1: Primary function name
            - fname2: Optional secondary function name
            - response_option: Response option (1/2/3)
            - option1: Value for fname1 (required if response_option=2)
            - option2: Value for fname2 (required if fname2 provided and response_option=2)

    Returns:
        Tuple of (success: bool, result_data or None, error_code or None)
    """
    logger.log_info("Starting automation workflow")

    try:
        # Extract parameters
        user_id = command_data.get('id')
        password = command_data.get('password')
        vin = command_data.get('vin')
        fname1 = command_data.get('fname1')
        fname2 = command_data.get('fname2')
        response_option = command_data.get('response_option')
        option1 = command_data.get('option1')
        option2 = command_data.get('option2')

        # Validate required parameters
        if not all([user_id, password, vin, fname1, response_option]):
            logger.log_fail("Missing required parameters")
            return False, None, ErrorCode.MISSING_REQUIRED_PARAMS

        processed_fnames = []

        # Step 1-2: Login (or skip if browser already at VIN input)
        if browser_manager.should_skip_login():
            logger.log_info("Skipping login - VIN input already visible")
        else:
            logger.log_info("Performing login")
            success, error = browser_manager.login_with_retry(user_id, password)
            if not success:
                return False, None, error

        # Step 3: VIN search
        success, error = search_vin(vin)
        if not success:
            return False, None, error

        # Step 4-7: Process fname1
        success, error = process_function_name(fname1, response_option, option1)
        if not success:
            logger.log_fail(f"Failed to process fname1: {fname1}")
            return False, None, error

        processed_fnames.append(fname1)

        # Step 8: Process fname2 (if provided)
        if fname2:
            logger.log_info("Processing fname2")

            # Navigate back to VIN search or detect state
            # For now, we'll search for the VIN again
            success, error = search_vin(vin)
            if not success:
                return False, None, error

            success, error = process_function_name(fname2, response_option, option2)
            if not success:
                logger.log_fail(f"Failed to process fname2: {fname2}")
                return False, None, error

            processed_fnames.append(fname2)

        # Build result data
        result_data = {
            'vin': vin,
            'fnames': processed_fnames,
            'response_type': response_option,
            'options': [option1] if not fname2 else [option1, option2]
        }

        logger.log_success("Automation workflow completed successfully")
        return True, result_data, None

    except Exception as e:
        logger.log_error("Unexpected error in automation workflow", e)
        return False, None, ErrorCode.UNKNOWN_ERROR
