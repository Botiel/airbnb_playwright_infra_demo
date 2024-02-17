import logging
from playwright.sync_api import Page, expect
from ..page_components.search_bar import SearchBarComponent


class HomePage:

    page_name = "Home Page"
    url = 'https://www.airbnb.com/'

    def __init__(self, page: Page):
        self.page = page
        self.search_bar = SearchBarComponent(page)

    @staticmethod
    def log(msg: str) -> None:
        logging.info(f'[Home Page] {msg}')

    def navigate_to_homepage(self) -> None:
        self.log("Navigating to airbnb homepage")
        self.page.goto('/', wait_until="load")

        self.log("Asserting page url")
        expect(self.page).to_have_url(self.url)
