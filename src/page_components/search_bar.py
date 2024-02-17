import datetime
import logging
from typing import Literal
from playwright.sync_api import Page, Locator
from ..utils.locators_object_base import LocatorsBase
from ..utils.constants import DATES_DICT
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


class Locators(LocatorsBase):
    is_expended_attrib = 'aria-expanded'
    increase_css = '[data-testid="stepper-{value}-increase-button"]'
    decrease_css = '[data-testid="stepper-{value}-decrease-button"]'

    def __init__(self, page: Page):
        super().__init__(page)

        self.root = page.locator('#search-tabpanel')
        self.list_option = page.get_by_role('listbox').get_by_role('option')
        self.search_dest_input = self.root.locator('#bigsearch-query-location-input')

        self.check_in_btn = self.get_data_test_id_locator("structured-search-input-field-split-dates-0")
        self.check_out_btn = self.get_data_test_id_locator("structured-search-input-field-split-dates-1")

        self.guests_btn = self.get_data_test_id_locator("structured-search-input-field-guests-button")
        self.guests_listbox = self.get_data_test_id_locator("structured-search-input-field-guests-panel")

        self.search_btn = self.get_data_test_id_locator("structured-search-input-search-button")
        self.little_search_bar = self.get_data_test_id_locator("little-search")

    def get_date_btn_locator(self, date: datetime.date) -> Locator:
        d = date.strftime('%d')
        m = date.strftime('%m')
        return self.page.locator(f'[data-testid="calendar-day-{m}/{d}/{date.year}"]')

    def get_guests_count_locator(self, value: str) -> Locator:
        return self.page.locator(f'[data-testid="stepper-{value}-value"]')


class SearchBarComponent:

    def __init__(self, page: Page):
        self.page = page
        self.locators = Locators(page)

    @staticmethod
    def log(msg: str) -> None:
        logging.info(f'[Search Bar] {msg}')

    def is_button_pressed(self, btn: Locator, name: str, to_click: bool = True) -> bool:
        self.log(f"Checking if {name} button is pressed")
        is_pressed = True if btn.get_attribute(self.locators.is_expended_attrib) == "true" else False

        if not is_pressed and to_click:
            self.log(f"Clicking {name} button")
            btn.click()

        return is_pressed

    def search_destination(self, value: str) -> None:
        self.log(f"inserting value to destination search: {value}")
        self.locators.search_dest_input.fill(value)
        option_locator = self.locators.list_option.filter(has_text=value).first
        option_locator.wait_for(state='visible')
        option_locator.click()

        self.log("Asserting input")
        intervals = 1000
        elapsed_time = 0
        timeout = 15 * 1000
        while self.locators.search_dest_input.get_attribute('value') == '':

            if timeout == elapsed_time:
                raise PlaywrightTimeoutError

            self.page.wait_for_timeout(intervals)
            elapsed_time += intervals

    def insert_dates(self, check_in: datetime.datetime, check_out: datetime.datetime) -> bool:
        """
        will only work for this month and the next one for now (due to home assignment requirements)

        :param check_in: datetime(2024, 2, 16)
        :param check_out: datetime(2024, 2, 17)
        :return:
        """
        self.log("Inserting Dates")

        now = datetime.datetime.now()

        if check_in.strftime('%m-%d-%Y') < now.strftime('%m-%d-%Y'):
            raise Exception('Please enter a valid check-in date')

        if check_out < now or check_out < check_in:
            raise Exception('Please enter a valid check-out date')

        # checking if the check in button is pressed
        self.is_button_pressed(self.locators.check_in_btn, name="check-in")

        checkin_locator = self.locators.get_date_btn_locator(check_in)
        self.page.wait_for_timeout(1000)
        checkout_locator = self.locators.get_date_btn_locator(check_out)

        if checkin_locator.is_enabled() and checkout_locator.is_enabled():
            checkin_locator.click()
            checkout_locator.click()
            return True

        self.log('Could not insert dates, one or more date is unavailable')
        return False

    def add_guests(
            self,
            guests: Literal['adults', 'children', 'infants', 'pets'],
            action: Literal['increase', 'decrease'],
            quantity: int
    ) -> None:

        self.log(f"Add Guests > {guests} > {action} > quantity: {quantity}")

        self.is_button_pressed(self.locators.guests_btn, name="Guests")
        self.locators.guests_listbox.wait_for(state="visible")

        match action:
            case 'increase':
                locator = self.page.locator(self.locators.increase_css.format(value=guests))
            case 'decrease':
                locator = self.page.locator(self.locators.decrease_css.format(value=guests))
            case _:
                raise Exception(f'No such action: {action}')

        for _ in range(quantity):
            locator.click()
            self.page.wait_for_timeout(500)

    def click_search_button(self) -> None:
        self.log("Clicking Search Button")
        self.locators.search_btn.click()
        self.page.wait_for_load_state(state="load")

    def expend_search_bar(self, wait_for_search_bar_timeout: int = 5000) -> bool:
        self.log('Trying to expand search bar')
        try:
            self.locators.little_search_bar.wait_for(state='visible', timeout=wait_for_search_bar_timeout)
        except PlaywrightTimeoutError:
            self.log('Did not expand search bar (Not visible)')
            return False
        else:
            self.log('Search bar expanded')
            self.locators.little_search_bar.click()
            self.page.wait_for_timeout(1000)
            return True

    def get_guests_count(self, guest: str) -> int:
        text = self.locators.get_guests_count_locator(guest).text_content()
        return int(text)

    def assert_search_location(self, value: str) -> None:
        self.log(f'Asserting location to be: {value}')
        input_value = self.locators.search_dest_input.get_attribute('value')
        assert value.lower() in input_value.lower()

    def assert_search_dates(self, check_in: datetime.datetime, check_out: datetime.datetime) -> None:
        in_text = self.locators.check_in_btn.text_content()
        out_text = self.locators.check_out_btn.text_content()

        in_date = f'{DATES_DICT.get(check_in.strftime("%B"))} {check_in.day}'
        out_date = f'{DATES_DICT.get(check_out.strftime("%B"))} {check_out.day}'

        self.log(f'Asserting checkin date to be: {in_date}')
        assert in_date in in_text

        self.log(f'Asserting checkout date to be: {out_date}')
        assert out_date in out_text

    def assert_guests(
            self,
            adults: int = 1,
            children: int = 0,
            infants: int = 0,
            pets: int = 0
    ) -> None:
        self.log(f'Asserting guests count > adults: {adults}, children: {children}, infants: {infants}, pets: {pets}')

        if adults == 0:
            raise ValueError('Adults count can not be 0')

        self.locators.guests_btn.click()
        assert self.get_guests_count('adults') == adults
        assert self.get_guests_count('children') == children
        assert self.get_guests_count('infants') == infants
        assert self.get_guests_count('pets') == pets
