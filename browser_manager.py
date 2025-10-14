"""
Browser Manager Module
Handles WebDriver lifecycle, element waiting, and browser state management
"""

from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import config
import logger
from error_codes import ErrorCode, get_error_message


# Global browser instance (singleton)
_browser_instance: Optional[webdriver.Chrome] = None


def start_browser() -> webdriver.Chrome:
    """
    Launch Chrome browser with configured options

    Returns:
        WebDriver instance

    Raises:
        WebDriverException: If browser fails to start
    """
    global _browser_instance

    if _browser_instance is not None:
        logger.log_info("Browser already running, returning existing instance")
        return _browser_instance

    logger.log_info("Starting Chrome browser...")

    try:
        # Configure Chrome options
        chrome_options = webdriver.ChromeOptions()

        # Headless MUST be False - buttons not visible in headless mode
        if config.BROWSER_OPTIONS['headless']:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument(f"--window-size={config.BROWSER_OPTIONS['window_size']}")

        if config.BROWSER_OPTIONS['disable_gpu']:
            chrome_options.add_argument('--disable-gpu')

        if config.BROWSER_OPTIONS['no_sandbox']:
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')

        # Additional options for stability
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Initialize ChromeDriver
        if config.CHROMEDRIVER_PATH:
            # Use specified ChromeDriver path (fastest - no download check)
            logger.log_info(f"Using ChromeDriver at: {config.CHROMEDRIVER_PATH}")
            service = Service(config.CHROMEDRIVER_PATH)
        else:
            # Use webdriver-manager (auto-download and cache)
            logger.log_info("Using webdriver-manager for ChromeDriver")
            service = Service(ChromeDriverManager().install())

        _browser_instance = webdriver.Chrome(service=service, options=chrome_options)

        # Maximize browser window to fullscreen
        _browser_instance.maximize_window()
        logger.log_info("Browser window maximized to fullscreen")

        # Set page load timeout
        _browser_instance.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)

        logger.log_success("Browser started successfully")
        return _browser_instance

    except Exception as e:
        logger.log_error("Failed to start browser", e)
        _browser_instance = None
        raise


def stop_browser():
    """
    Close browser and quit WebDriver
    """
    global _browser_instance

    if _browser_instance is None:
        logger.log_info("No browser instance to stop")
        return

    logger.log_info("Stopping browser...")

    try:
        _browser_instance.quit()
        logger.log_success("Browser stopped successfully")
    except Exception as e:
        logger.log_error("Error stopping browser", e)
    finally:
        _browser_instance = None


def get_browser() -> Optional[webdriver.Chrome]:
    """
    Get current WebDriver instance (singleton pattern)

    Returns:
        WebDriver instance or None if not started
    """
    return _browser_instance


def is_browser_running() -> bool:
    """
    Check if browser is active

    Returns:
        True if browser is running, False otherwise
    """
    if _browser_instance is None:
        return False

    try:
        # Try to get current URL to verify browser is responsive
        _ = _browser_instance.current_url
        return True
    except:
        return False


def is_browser_crashed() -> bool:
    """
    Detect if browser has crashed

    Returns:
        True if browser crashed, False otherwise
    """
    global _browser_instance

    if _browser_instance is None:
        return False

    try:
        # Try to access browser properties
        _ = _browser_instance.current_url
        _ = _browser_instance.title
        return False
    except WebDriverException:
        logger.log_fail("Browser crash detected")
        _browser_instance = None
        return True
    except:
        return False


def restart_browser() -> webdriver.Chrome:
    """
    Stop and start browser (clears session)

    Returns:
        New WebDriver instance
    """
    logger.log_info("Restarting browser...")
    stop_browser()
    return start_browser()


def detect_browser_state() -> str:
    """
    Check current browser state and page

    Returns:
        State string: 'vin_input_visible', 'login_page', 'unknown', or 'not_running'
    """
    if not is_browser_running():
        return 'not_running'

    browser = get_browser()
    if browser is None:
        return 'not_running'

    try:
        # Check if VIN input is visible
        vin_input = browser.find_elements(By.CSS_SELECTOR, config.SELECTORS['vin_input'])
        if vin_input and vin_input[0].is_displayed():
            logger.log_info("Browser state: VIN input visible")
            return 'vin_input_visible'

        # Check if on login page
        current_url = browser.current_url
        if 'login' in current_url.lower():
            logger.log_info("Browser state: Login page")
            return 'login_page'

        logger.log_info(f"Browser state: Unknown (URL: {current_url})")
        return 'unknown'

    except Exception as e:
        logger.log_error("Error detecting browser state", e)
        return 'unknown'


def should_skip_login() -> bool:
    """
    Check if browser is running and VIN input field is visible
    (indicating we can skip login steps)

    Returns:
        True if both conditions met, False otherwise
    """
    if not is_browser_running():
        return False

    state = detect_browser_state()
    return state == 'vin_input_visible'


def set_zoom_level(zoom: float = 0.8):
    """
    Set browser zoom level

    Args:
        zoom: Zoom level (e.g., 0.8 for 80%, 1.0 for 100%)
    """
    browser = get_browser()
    if browser is None:
        return

    try:
        browser.execute_script(f"document.body.style.zoom='{zoom}'")
        logger.log_info(f"Browser zoom level set to {int(zoom * 100)}%")
    except Exception as e:
        logger.log_info(f"Could not set zoom level: {e}")


def wait_for_element(
    selector: str,
    by: By = By.CSS_SELECTOR,
    timeout: int = config.ELEMENT_WAIT_TIMEOUT
) -> Tuple[bool, Optional[object], Optional[ErrorCode]]:
    """
    Wait for element to appear with timeout

    Args:
        selector: Element selector
        by: Selenium By locator type (default: CSS_SELECTOR)
        timeout: Wait timeout in seconds (default: from config)

    Returns:
        Tuple of (success: bool, element or None, error_code or None)
    """
    browser = get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, None, ErrorCode.BROWSER_CRASH

    try:
        logger.log_info(f"Waiting for element: {selector}")
        element = WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        logger.log_success(f"Element found: {selector}")
        return True, element, None

    except TimeoutException:
        logger.log_fail(f"Timeout waiting for element: {selector}")
        return False, None, ErrorCode.ELEMENT_WAIT_TIMEOUT

    except Exception as e:
        logger.log_error(f"Error waiting for element: {selector}", e)
        return False, None, ErrorCode.UNKNOWN_ERROR


def wait_for_clickable(
    selector: str,
    by: By = By.CSS_SELECTOR,
    timeout: int = config.ELEMENT_WAIT_TIMEOUT
) -> Tuple[bool, Optional[object], Optional[ErrorCode]]:
    """
    Wait for element to be clickable (visible and enabled) with timeout

    Args:
        selector: Element selector
        by: Selenium By locator type (default: CSS_SELECTOR)
        timeout: Wait timeout in seconds (default: from config)

    Returns:
        Tuple of (success: bool, element or None, error_code or None)
    """
    browser = get_browser()
    if browser is None:
        logger.log_fail("Browser not running")
        return False, None, ErrorCode.BROWSER_CRASH

    try:
        logger.log_info(f"Waiting for clickable element: {selector}")
        element = WebDriverWait(browser, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        logger.log_success(f"Element is clickable: {selector}")
        return True, element, None

    except TimeoutException:
        logger.log_fail(f"Timeout waiting for clickable element: {selector}")
        return False, None, ErrorCode.ELEMENT_WAIT_TIMEOUT

    except Exception as e:
        logger.log_error(f"Error waiting for clickable element: {selector}", e)
        return False, None, ErrorCode.UNKNOWN_ERROR


def login_with_retry(user_id: str, password: str) -> Tuple[bool, Optional[ErrorCode]]:
    """
    Navigate to login page, fill credentials, submit, and retry on failure

    Args:
        user_id: Login username
        password: Login password

    Returns:
        Tuple of (success: bool, error_code or None)
    """
    max_retries = config.MAX_LOGIN_RETRIES
    attempt = 0

    while attempt <= max_retries:
        attempt += 1
        logger.log_info(f"Login attempt {attempt}/{max_retries + 1}")

        try:
            browser = get_browser()
            if browser is None:
                browser = start_browser()

            # Navigate to login page
            logger.log_info(f"Navigating to {config.TARGET_URL}")
            browser.get(config.TARGET_URL)

            # Set zoom level after page load
            set_zoom_level(0.8)

            # Wait for login form
            success, id_field, error = wait_for_element(config.SELECTORS['login_id'])
            if not success:
                logger.log_fail("Login form not found")
                if attempt <= max_retries:
                    restart_browser()
                    continue
                return False, ErrorCode.ELEMENT_WAIT_TIMEOUT

            # Fill username
            logger.log_info("Filling username")
            logger.debug_sleep(config.DEBUG_INTERVAL, "Before filling username")
            id_field.clear()
            id_field.send_keys(user_id)

            # Wait for password field
            success, pw_field, error = wait_for_element(config.SELECTORS['login_pw'])
            if not success:
                logger.log_fail("Password field not found")
                if attempt <= max_retries:
                    restart_browser()
                    continue
                return False, ErrorCode.ELEMENT_WAIT_TIMEOUT

            # Fill password
            logger.log_info("Filling password")
            logger.debug_sleep(config.DEBUG_INTERVAL, "Before filling password")
            pw_field.clear()
            pw_field.send_keys(password)

            # Wait for login button to be clickable
            logger.debug_sleep(config.DEBUG_INTERVAL, "Before clicking login button")

            success, login_btn, error = wait_for_clickable(config.SELECTORS['login_button'])
            if not success:
                logger.log_fail("Login button not clickable")
                if attempt <= max_retries:
                    restart_browser()
                    continue
                return False, ErrorCode.ELEMENT_WAIT_TIMEOUT

            logger.log_info("Clicking login button")
            login_btn.click()

            # Wait a moment for page transition
            import time
            time.sleep(2)

            # Check if login succeeded by looking for VIN input or checking URL
            current_url = browser.current_url
            if 'login' not in current_url.lower():
                logger.log_success("Login successful")
                # Set zoom level on the main page after login
                set_zoom_level(0.8)
                return True, None

            # Still on login page - login failed
            logger.log_fail(f"Login failed (still on login page)")

            if attempt <= max_retries:
                logger.log_info("Restarting browser for retry")
                restart_browser()
            else:
                logger.log_fail("Maximum login retries exceeded")
                return False, ErrorCode.LOGIN_FAILURE

        except Exception as e:
            logger.log_error(f"Login attempt {attempt} failed with exception", e)

            if attempt <= max_retries:
                try:
                    restart_browser()
                except:
                    pass
            else:
                return False, ErrorCode.LOGIN_FAILURE

    return False, ErrorCode.LOGIN_FAILURE
