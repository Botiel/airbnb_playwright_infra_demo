import logging
from playwright.sync_api import Page
from ..page_components.search_bar import SearchBarComponent
from ..utils.locators_object_base import LocatorsBase
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class Locators(LocatorsBase):

    def __init__(self, page: Page):
        super().__init__(page)

        self.translation_popup = page.get_by_label("Translation on")
        self.close_popup_btn = self.translation_popup.get_by_role('button', name='Close')
        self.reserve_btn = page.locator('[data-testid="book-it-default"]').locator('[data-testid="homes-pdp-cta-btn"]')


class ApartmentPage:

    page_name = "Apartment Page"

    def __init__(self, page: Page):
        self.page = page
        self.search_bar = SearchBarComponent(page)
        self.locators = Locators(page)

    @staticmethod
    def log(msg: str) -> None:
        logging.info(f'[Apartment Page] {msg}')

    def check_for_translation_popup(self, timeout: int = 3000) -> None:
        self.log('Waiting for translation popup')
        try:
            self.locators.translation_popup.wait_for(state='visible', timeout=timeout)
        except PlaywrightTimeoutError:
            return

        self.log('Closing popup')
        self.locators.close_popup_btn.click()

    def validate_navigation_to_apartment_page(self) -> None:
        self.log('Asserting navigation to apartment page')
        room = "https://www.airbnb.com/room"
        luxury = "https://www.airbnb.com/luxury"
        current = self.page.url
        assert current.startswith(room) or current.startswith(luxury)

    def click_reserve_button(self) -> None:
        self.log('Clicking Reserve button')
        for btn in self.locators.reserve_btn.all():
            if btn.is_visible() and btn.is_enabled():
                btn.click()
                return
