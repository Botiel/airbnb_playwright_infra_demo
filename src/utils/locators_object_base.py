from playwright.sync_api import Page, Locator


class LocatorsBase:

    def __init__(self, page: Page):
        self.page = page

    def get_data_test_id_locator(self, value: str) -> Locator:
        return self.page.locator(f'[data-testid="{value}"]')
