"""
Configuration constants for TCP-Controlled Web Browser Automation Module
"""

# URL Constants
TARGET_URL = "https://shisaku.infra.tc/login"
TESTS_URL = "https://shisaku.infra.tc/tests"
PUSH_COMMAND_URL = "https://shisaku.infra.tc/push-command"

# TCP Server Configuration
DEFAULT_TCP_PORT = 5000

# Timeout Constants (in seconds)
ELEMENT_WAIT_TIMEOUT = 30
PAGE_LOAD_TIMEOUT = 30

# CSS Selectors
SELECTORS = {
    # Login page
    'login_id': '#input-1',
    'login_pw': '#input-2',
    'login_button': 'body > div > div > div.login-container > div > div.card-body > p > form > button',

    # VIN search
    'vin_input': '#vin-input',
    'vin_result_row': 'td[aria-colindex="3"]',

    # Function name search
    'function_name_cell': 'td[aria-colindex="3"]',

    # Radio buttons for response options
    'radio_default': 'tsp-response-radio-group0_BV_option_0',           # option 1
    'radio_custom': 'tsp-response-radio-group0_BV_option_1',            # option 2
    'radio_no_response': 'tsp-response-radio-group0_BV_option_2',       # option 3

    # JSON editing
    'json_textarea': '#textarea-formatter-0',

    # Update button - using class selector for more reliable matching
    'update_button': 'button.update-button.btn-success',

    # Push command page selectors
    'push_devices_input': '#push-devices-input',
    'push_topic_dropdown': '#input-4',
    'push_topic_dropdown_xpath': '//*[@id="input-group-3"]//select[@id="input-4"]',
    'push_response_topic_dropdown_xpath': '//*[@id="input-group-5"]//select[@id="input-4"]',
    'push_template_dropdown': '#input-6',
    'push_send_button': '.btn.update-button.btn-success',
    'push_success_alert': '.alert-success'
}

# Push command textarea fallback selectors (dynamic __BVID__ ID workaround)
PUSH_TEXTAREA_FALLBACKS = [
    "div.card-body div.container div.row div.col textarea.form-control",
    "textarea.form-control[rows='6'][wrap='soft']",
    "textarea[data-v-4efe8a10]",
    "div.card-body textarea",
    "textarea.form-control",
]

# Browser Configuration
BROWSER_OPTIONS = {
    'headless': True,   # Non-headless mode (browser window visible)
    'window_size': '1920,1080',
    'disable_gpu': True,
    'no_sandbox': True
}

# Retry Configuration
MAX_LOGIN_RETRIES = 2
MAX_START_RETRIES = 3

# Debug Configuration
DEBUG_MODE = False  # Set to True to enable 2-second delays between operations
DEBUG_INTERVAL = 2.0  # Seconds to wait between operations in debug mode

# ChromeDriver Configuration
CHROMEDRIVER_PATH = None  # Set to chromedriver.exe path to skip auto-download
# Example: CHROMEDRIVER_PATH = r"C:\path\to\chromedriver.exe"
