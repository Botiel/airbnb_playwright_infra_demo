import re
import logging
import datetime
from playwright.sync_api import Page, Locator
from ..page_components.search_bar import SearchBarComponent
from ..page_components.pagination_bar import PaginationBarComponent
from ..utils.locators_object_base import LocatorsBase
from dataclasses import dataclass
from ..utils.helper_methods import (
    wait_for_result_cards_to_load,
    extract_link_from_result_card,
    extract_rating_from_result_card
)


@dataclass(kw_only=True)
class CardInfo:
    locator: Locator
    page_number: int
    rating: float
    url: str


class Locators(LocatorsBase):

    def __init__(self, page: Page):
        super().__init__(page)

        self.results_header = page.locator('//span[contains(text(), "Search results")]')
        self.filter_btn = self.get_data_test_id_locator("category-bar-filter-button")
        self.filters_form = page.locator('[data-testid="modal-container"]').get_by_label("Filters")
        self.guest_favorite_btn = self.filters_form.get_by_role('button').filter(has_text="Guest favorites")
        self.show_filter_btn = self.filters_form.locator('a').filter(
            has=page.get_by_text(re.compile(r'Show.*?(\d+).*?places'))
        )
        self.card_container = self.get_data_test_id_locator("card-container")


class ResultsPage:
    page_name = "Results Page"
    location_url = 'https://www.airbnb.com/s/{location}'
    url_dates_string = 'calendar&checkin={checkin}&checkout={checkout}'
    time_format = "%Y-%m-%d"

    def __init__(self, page: Page):
        self.page = page
        self.locators = Locators(page)
        self.search_bar = SearchBarComponent(page)
        self.pagination_bar = PaginationBarComponent(page)

    @staticmethod
    def log(msg: str) -> None:
        logging.info(f'[Results Page] {msg}')

    def assert_guests_in_url_link(
        self,
            adults: int = 1,
            children: int = None,
            infants: int = None,
            pets: int = None
    ) -> None:

        if adults == 0:
            raise ValueError('Adults count can not be 0')

        li = [f'adults={adults}']
        if children:
            li.append(f'children={children}')

        if infants:
            li.append(f'infants={infants}')

        if pets:
            li.append(f'pets={pets}')

        for item in li:
            assert item in self.page.url

    def validate_navigation_to_results_page(
            self,
            check_in: datetime.datetime,
            check_out: datetime.datetime,
            location: str,
    ) -> None:
        """

        :param check_in: datetime(2024, 2, 16)
        :param check_out: datetime(2024, 2, 17)
        :param location: city / country
        :return:
        """

        current_url = self.page.url

        assert self.location_url.format(location=location.title()) in current_url

        url_dates = self.url_dates_string.format(
            checkin=check_in.strftime(self.time_format),
            checkout=check_out.strftime(self.time_format)
        )

        assert url_dates in current_url

    def check_for_results_count(self) -> int | None:
        self.locators.results_header.wait_for(state='visible')
        text = self.locators.results_header.text_content().split(" ")
        numbers = [int(item) for item in text if item.isdigit()]
        return numbers[0] if numbers else None

    def filter_results_by_highest_rate(self) -> None:
        self.locators.filter_btn.click()
        self.locators.filters_form.wait_for(state="visible")
        self.locators.guest_favorite_btn.scroll_into_view_if_needed()
        self.locators.guest_favorite_btn.click()
        self.locators.show_filter_btn.click()
        wait_for_result_cards_to_load(self.page, self.page_name)

    def get_highest_score_listing(self) -> list[CardInfo]:

        highest_score = []
        current_page = 1

        while True:

            card_li = self.locators.card_container.all()
            if not card_li:
                raise Exception('There are no listing cards...')

            for card in card_li:

                rating = extract_rating_from_result_card(card)
                if rating is None:
                    continue

                if not highest_score or rating == highest_score[0].rating:
                    highest_score.append(
                        CardInfo(
                            locator=card,
                            rating=rating,
                            page_number=current_page,
                            url=extract_link_from_result_card(card)
                        )
                    )

                elif rating > highest_score[0].rating:
                    highest_score.clear()
                    highest_score.append(
                        CardInfo(
                            locator=card,
                            rating=rating,
                            page_number=current_page,
                            url=extract_link_from_result_card(card)
                        )
                    )

            if not self.pagination_bar.is_pagination_bar_visible():
                break

            if not self.pagination_bar.paginate_right():
                break
            else:
                current_page += 1

        return highest_score

    def navigate_to_card_page(self, card_info: CardInfo) -> None:
        self.log(f'Navigating to card page: {card_info.url}')
        self.page.goto(card_info.url)
        self.page.wait_for_load_state(state="load")

    def get_highest_listing_flow(self) -> None:
        self.filter_results_by_highest_rate()
        results_li = self.get_highest_score_listing()

        if not results_li:
            raise Exception(f'[{self.page_name}] Something went wrong, no results were found')

        # navigating to the first highest rating card
        self.log('Navigating to highest rating listing')
        self.navigate_to_card_page(results_li[0])
