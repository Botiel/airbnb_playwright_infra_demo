
import pytest
from playwright.sync_api import BrowserContext, Browser
from typing import Generator
from pathlib import Path
import importlib
from src.extended_pytest_playwright import create_extended_options, init_context, handle_artifacts
from src.airbnb_manager import AirbnbManager


ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------- FIXTURES ---------------------------------------------------------

@pytest.fixture
def extended_context(
        browser: Browser,
        browser_context_args: dict,
        pytestconfig: pytest.Config,
        request: pytest.FixtureRequest,
        browser_name: str
) -> Generator[BrowserContext, None, None]:

    context, pages = init_context(
        browser=browser,
        browser_context_args=browser_context_args,
        pytestconfig=pytestconfig,
        request=request,
        browser_name=browser_name
    )

    yield context

    handle_artifacts(
        context=context,
        pytestconfig=pytestconfig,
        request=request,
        pages=pages
    )


@pytest.fixture
def get_manager(
        extended_context: BrowserContext,
        request: pytest.FixtureRequest
) -> Generator[AirbnbManager, None, None]:
    page = extended_context.new_page()
    yield AirbnbManager(page)


# ------------------------------------------------HOOKS-----------------------------------------------------------------
def pytest_addoption(parser: pytest.Parser) -> None:
    create_extended_options(parser)


def pytest_itemcollected(item: pytest.Item) -> None:
    # Changing test name  web browser suffix: [browser] -> _browser
    # Set the modified test name
    new_test_name = item.nodeid.replace('[', '_').replace(']', '')
    item._nodeid = new_test_name


def pytest_configure(config: pytest.Config) -> None:
    # For running and debugging tests from pycharm

    if config.getoption('--use-pycharm-debugger-args'):

        # Importing the configurations file from project root
        module_name = "pytest_configurations"
        my_module = importlib.import_module(module_name, package=str(ROOT))
        configurations = my_module.configurations

        # Credentials and configurations from configurations file
        config.option.base_url = configurations.base_url
        config.option.password = configurations.password
        config.option.username = configurations.username
        config.option.headed = configurations.headed
        config.option.browser_channel = configurations.browser_channel

        # Debugger static configurations
        config.option.viewport = [["1600", "900"]]
        config.option.log_cli_level = "DEBUG"
        config.option.tracing = "off"
        config.option.video = "off"
        config.option.screenshot = "off"

        print(config.option)
