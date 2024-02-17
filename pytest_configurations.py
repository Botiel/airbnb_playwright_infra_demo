
from pathlib import Path
from src.extended_pytest_playwright import (
    PytestConfigurationsBase,
    State,
    Browser,
    BrowserChannel,
    LogCli,
    RunTestBy,
    ViewPort,
    RunTestObject
)

ROOT = Path(__file__).resolve().parent

configurations = PytestConfigurationsBase(

        # Credentials
        base_url='https://www.airbnb.com/',
        username='',
        password='',

        # Test setup
        headed=False,
        log_cli_level=LogCli.INFO,
        browsers=[Browser.CHROMIUM, Browser.FIREFOX, Browser.WEBKIT],
        tracing=State.ON,
        video=State.ON,
        screenshot=State.ONLY_ON_FAILURE,
        full_page_screenshot=False,
        browser_channel=None,

        # General configurations
        viewport=ViewPort(height=900, width=1600),
        navigation_timeout=60 * 1000,
        default_timeout=15 * 1000,
        ignore_https_errors=True,
        use_storage_state=False,
        clipboard_permissions=True,
        workers=3,

        # Root and Reports Folder
        root_folder=ROOT,
        reports_folder_pattern=ROOT / 'pytest_reports' / 'test-report'
)

tests = RunTestObject(
    run_by=RunTestBy.FILE,
    tests=["tests/test_airbnb_flows.py"]
)
