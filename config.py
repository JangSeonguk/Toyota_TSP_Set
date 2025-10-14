"""
Configuration constants for TCP-Controlled Web Browser Automation Module
"""

# URL Constants
TARGET_URL = "https://shisaku.infra.tc/login"

# TCP Server Configuration
DEFAULT_TCP_PORT = 5000

# Timeout Constants (in seconds)
ELEMENT_WAIT_TIMEOUT = 10
PAGE_LOAD_TIMEOUT = 30

# CSS Selectors
SELECTORS = {
    # Login page
    'login_id': '#input-1',
    'login_pw': '#input-2',
    'login_button': 'body > div > div > div.login-container > div > div.card-body > p > form > button',

    # VIN search
    'vin_input': '#vin-input',
    'vin_result_row': 'div.shisaku-table > table > tbody > tr',

    # Function name search
    'function_name_cell': 'td[aria-colindex="3"]',

    # Radio buttons for response options
    'radio_default': 'tsp-response-radio-group0_BV_option_0',           # option 1
    'radio_custom': 'tsp-response-radio-group0_BV_option_1',            # option 2
    'radio_no_response': 'tsp-response-radio-group0_BV_option_2',       # option 3

    # JSON editing
    'json_textarea': '#textarea-formatter-0',

    # Update button - using class selector for more reliable matching
    'update_button': 'button.update-button.btn-success'
}

# Browser Configuration
BROWSER_OPTIONS = {
    'headless': False,  # Must be False - buttons not visible in headless mode
    'window_size': '1920,1080',
    'disable_gpu': True,
    'no_sandbox': True
}

# Retry Configuration
MAX_LOGIN_RETRIES = 2

# Debug Configuration
DEBUG_MODE = False  # Set to True to enable 2-second delays between operations
DEBUG_INTERVAL = 2.0  # Seconds to wait between operations in debug mode

# ChromeDriver Configuration
CHROMEDRIVER_PATH = None  # Set to chromedriver.exe path to skip auto-download
# Example: CHROMEDRIVER_PATH = r"C:\path\to\chromedriver.exe"
