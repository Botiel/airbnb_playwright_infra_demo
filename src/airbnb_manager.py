from playwright.sync_api import Page
from .page_objects.home_page import HomePage
from .page_objects.results_page import ResultsPage
from .page_objects.apartment_page import ApartmentPage
from .page_objects.reservation_page import ReservationPage


class AirbnbManager:

    def __init__(self, page: Page):
        self.page = page

        self.home_page = HomePage(page)
        self.results_page = ResultsPage(page)
        self.apartment_page = ApartmentPage(page)
        self.reservation_page = ReservationPage(page)
