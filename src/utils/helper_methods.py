import logging
from playwright.sync_api import Page, Locator


def wait_for_result_cards_to_load(page: Page, page_name: str, timeout: int = 500) -> None:
    logging.info(f'[{page_name}] Waiting for results to load')
    card = page.locator('[data-testid="card-container"]')
    card.first.wait_for(state='visible')

    # minor timeout so the pagination won't be too fast
    page.wait_for_timeout(timeout)


def extract_rating_from_result_card(card: Locator) -> float | None:
    card.wait_for(state='visible')
    text = card.text_content().split("breakdown")[-1].split(" ")[0]

    try:
        rating = float(text)
    except ValueError:
        return

    return rating


def extract_link_from_result_card(card: Locator) -> str:
    card.wait_for(state='visible')
    link = card.locator('a').first.get_attribute('href')
    return f'https://airbnb.com{link}'
