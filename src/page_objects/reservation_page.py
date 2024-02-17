import logging
from playwright.sync_api import Page
from ..utils.locators_object_base import LocatorsBase


class Locators(LocatorsBase):

    def __init__(self, page: Page):
        super().__init__(page)
        self.confirm_title = page.locator('[data-section-id="DESKTOP_TITLE"]')


class ReservationPage:

    page_name = "Reservation Page"
    url = 'https://www.airbnb.com/book'
    adults_url_string = "numberOfAdults={count}"

    def __init__(self, page: Page):
        self.page = page
        self.locators = Locators(page)

    @staticmethod
    def log(msg: str) -> None:
        logging.info(f'[Reservation Page] {msg}')

    def wait_for_page_to_load(self) -> None:
        self.log('Waiting for page title to be visible')
        self.locators.confirm_title.wait_for(state='visible')

    def assert_adults_count_in_url(self, count: int) -> None:
        self.log(f'Asserting adults count to be {count} in the url')
        if count < 1:
            raise ValueError('Adults count can not be lower than 1')
        assert self.adults_url_string.format(count=count) in self.page.url

    def assert_reservation_page_url(self) -> None:
        self.log('Asserting reservations url')
        assert self.page.url.startswith(self.url)
