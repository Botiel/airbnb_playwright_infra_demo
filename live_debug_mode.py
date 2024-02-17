
import logging
from datetime import datetime as dt
from src.airbnb_manager import AirbnbManager
from pytest_configurations import configurations
from playwright.sync_api import (
    sync_playwright,
    Page,
    BrowserContext,
    Browser,
    expect,
    Locator
)
from src.utils.helper_methods import (
    extract_rating_from_result_card,
    extract_link_from_result_card,
    wait_for_result_cards_to_load
)


def main():

    logging.basicConfig(level=logging.DEBUG)

    with sync_playwright() as p:

        browser: Browser = p.chromium.launch(headless=False)

        context: BrowserContext = browser.new_context(
            viewport={'height': 900, 'width': 1600},
            ignore_https_errors=True,
            base_url=configurations.base_url,
        )

        context.set_default_navigation_timeout(timeout=45 * 1000)
        context.set_default_timeout(timeout=4000)
        context.grant_permissions(['clipboard-write', 'clipboard-read'])

        page: Page = context.new_page()
        m = AirbnbManager(page)
        m.home_page.navigate_to_homepage()

        print('Debug BreakPoint')
        breakpoint()


if __name__ == '__main__':
    main()
