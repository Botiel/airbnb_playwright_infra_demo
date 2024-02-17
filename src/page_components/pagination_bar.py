import logging
from playwright.sync_api import Page, Locator
from ..utils.locators_object_base import LocatorsBase
from ..utils.helper_methods import wait_for_result_cards_to_load
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class Locators(LocatorsBase):

    disabled_attrib = "aria-disabled"

    def __init__(self, page: Page):
        super().__init__(page)

        self.root = page.get_by_label("Search results pagination")
        self.paginate_right_btn = self.root.get_by_label('Next')
        self.paginate_left_btn = self.root.get_by_label('Previous')
        self.current_page_btn = self.root.locator('button[aria-current="page"]')

    def get_page_locator_by_number(self, number: int) -> Locator:
        return self.root.locator('a').filter(has_text=str(number))


class PaginationBarComponent:

    component_name = "Pagination Bar"

    def __init__(self, page: Page):
        self.page = page
        self.locators = Locators(page)

    @staticmethod
    def log(msg: str) -> None:
        logging.info(f'[Pagination Bar] {msg}')

    def get_current_page_number(self) -> int:
        return int(self.locators.current_page_btn.text_content())

    def is_button_disabled(self) -> bool:
        return self.locators.paginate_right_btn.get_attribute(self.locators.disabled_attrib) == "true"

    def paginate_right(self) -> bool:
        self.log('Paginating right')

        if self.is_button_disabled():
            self.log('Can not paginate to the right')
            return False

        before_pagination = self.get_current_page_number()
        self.log(f'Current page: {before_pagination}')
        _next = before_pagination + 1
        pressed = self.locators.current_page_btn.get_by_text(str(_next))

        self.locators.paginate_right_btn.click()

        try:
            pressed.wait_for(state='visible')
        except PlaywrightTimeoutError:
            raise PlaywrightTimeoutError('Pagination Failed')

        self.log(f'Paginated to page: {_next}')
        wait_for_result_cards_to_load(self.page, self.component_name)
        return True

    def paginate_left(self) -> bool:
        self.log('Paginating left')

        before_pagination = self.get_current_page_number()

        if before_pagination == 1:
            self.log('Can not paginate to the left')
            return False

        self.log(f'Current page: {before_pagination}')
        previous = before_pagination - 1
        pressed = self.locators.current_page_btn.get_by_text(str(previous))
        self.locators.paginate_left_btn.click()

        try:
            pressed.wait_for(state='visible')
        except PlaywrightTimeoutError:
            raise PlaywrightTimeoutError('Pagination Failed')

        self.log(f'Paginated to page: {previous}')
        wait_for_result_cards_to_load(self.page, self.component_name)
        return True

    def is_pagination_bar_visible(self) -> bool:
        return self.locators.root.is_visible()
