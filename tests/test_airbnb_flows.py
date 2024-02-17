import logging
import pytest
from datetime import datetime, timedelta

TODAY = datetime.now()
TOMORROW = TODAY + timedelta(days=1)
LOCATION = 'Amsterdam'
ADULTS = 2
CHILDREN = 1


@pytest.fixture(scope='function')
def before_each_test(get_manager):

    m = get_manager
    search = m.home_page.search_bar

    m.home_page.navigate_to_homepage()
    search.search_destination(LOCATION)
    search.insert_dates(check_in=TODAY, check_out=TOMORROW)
    search.add_guests(guests='adults', action='increase', quantity=ADULTS)
    search.add_guests(guests='children', action='increase', quantity=CHILDREN)
    search.click_search_button()

    m.results_page.validate_navigation_to_results_page(check_in=TODAY, check_out=TOMORROW, location=LOCATION)
    m.results_page.assert_guests_in_url_link(adults=ADULTS, children=CHILDREN)


def test_get_highest_rating_page(before_each_test, get_manager):
    m = get_manager
    m.results_page.get_highest_listing_flow()


def test_confirm_booking_details(before_each_test, get_manager):
    m = get_manager
    search = m.results_page.search_bar

    search.expend_search_bar()
    search.assert_search_location(LOCATION)
    search.assert_search_dates(TODAY, TOMORROW)
    search.assert_guests(ADULTS, CHILDREN)


def test_change_booking_guests(before_each_test, get_manager):
    m = get_manager
    search = m.results_page.search_bar

    search.expend_search_bar()
    search.assert_guests(ADULTS, CHILDREN)

    search.add_guests(guests='children', action='decrease', quantity=1)
    search.click_search_button()

    search.expend_search_bar()
    search.assert_guests(ADULTS, children=0)


def test_change_booking_dates(before_each_test, get_manager):
    m = get_manager
    search = m.results_page.search_bar

    search.expend_search_bar()

    in_a_week = TODAY + timedelta(weeks=1)
    logging.info(
        f'[test_change_booking_dates] trying to change checkout to a week from now: {in_a_week.strftime("%Y-%m-%d")}'
    )

    checkout_final_date = in_a_week
    is_inserted = search.insert_dates(check_in=TODAY, check_out=in_a_week)
    if not is_inserted:
        search.insert_dates(check_in=TODAY, check_out=TOMORROW)
        checkout_final_date = TOMORROW

    search.click_search_button()
    search.expend_search_bar()
    search.assert_search_dates(TODAY, checkout_final_date)


def test_booking_reservation(before_each_test, get_manager):
    m = get_manager

    m.results_page.get_highest_listing_flow()
    m.apartment_page.check_for_translation_popup()
    m.apartment_page.validate_navigation_to_apartment_page()
    m.apartment_page.click_reserve_button()
    m.reservation_page.wait_for_page_to_load()
    m.reservation_page.assert_reservation_page_url()
    m.reservation_page.assert_adults_count_in_url(count=ADULTS)
