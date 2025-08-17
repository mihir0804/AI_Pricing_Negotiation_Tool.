from prefect import flow, task
from playwright.sync_api import sync_playwright, Page, expect
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import logging
from typing import List, Dict

from etl.common.db import engine
from etl.common.schemas import CompetitorPriceRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration for Scrapers ---
# In a real project, this would be more sophisticated, maybe stored in a DB.
COMPETITOR_CONFIG = {
    "CompetitorA": {
        "base_url": "https://www.competitorA.com/products/",
        "price_selector": ".product-price",
        "stock_selector": ".stock-status"
    },
    "CompetitorB": {
        "base_url": "https://www.competitorB.com/",
        "price_selector": "#price",
        "stock_selector": "button[data-action='add-to-cart']"
    }
}


@task(retries=2, retry_delay_seconds=10)
def get_products_to_scrape() -> List[Dict]:
    """Fetches products from the database to be scraped."""
    logger.info("Fetching products to scrape from the database.")
    query = "SELECT sku, name FROM products;"
    with engine.connect() as conn:
        products = conn.execute(query).mappings().all()
    logger.info(f"Found {len(products)} products to scrape.")
    return products


@task
def fetch_prices_for_product(product: Dict, competitor: str) -> List[CompetitorPriceRecord]:
    """
    Scrapes a single product page for a given competitor.
    This is a placeholder and will not actually make a network request.
    """
    config = COMPETITOR_CONFIG[competitor]
    logger.info(f"Scraping '{product['name']}' from {competitor}...")

    # --- MOCK IMPLEMENTATION ---
    # In a real implementation, you would use Playwright here.
    # with sync_playwright() as p:
    #     browser = p.chromium.launch()
    #     page = browser.new_page()
    #     try:
    #         url = f"{config['base_url']}{product['sku']}"
    #         page.goto(url, wait_until="domcontentloaded")
    #         price_str = page.locator(config['price_selector']).inner_text()
    #         # ... parsing and stock check logic ...
    #         browser.close()
    #     except Exception as e:
    #         logger.error(f"Failed to scrape {product['sku']} from {competitor}: {e}")
    #         browser.close()
    #         return []

    # Using mock data instead of real scraping for this example.
    mock_price = 199.99 + hash(product['sku'] + competitor) % 50
    mock_in_stock = (hash(product['name']) % 10) > 1 # 90% in stock

    try:
        record = CompetitorPriceRecord(
            sku=product['sku'],
            competitor_name=competitor,
            price=mock_price,
            in_stock=mock_in_stock,
        )
        return [record]
    except ValidationError as e:
        logger.error(f"Validation failed for scraped data: {e}")
        return []


@task
def upsert_prices(records: List[CompetitorPriceRecord]):
    """Upserts a list of price records into the database."""
    if not records:
        logger.info("No records to upsert.")
        return

    logger.info(f"Upserting {len(records)} price records.")
    df = pd.DataFrame([r.dict() for r in records])

    # Get product_id and competitor_id from the database
    with engine.connect() as conn:
        products_map = pd.read_sql("SELECT sku, product_id FROM products", conn).set_index('sku')['product_id'].to_dict()
        competitors_map = pd.read_sql("SELECT name, competitor_id FROM competitors", conn).set_index('name')['competitor_id'].to_dict()

    df['product_id'] = df['sku'].map(products_map)
    df['competitor_id'] = df['competitor_name'].map(competitors_map)
    df.dropna(subset=['product_id', 'competitor_id'], inplace=True)
    df['product_id'] = df['product_id'].astype(int)
    df['competitor_id'] = df['competitor_id'].astype(int)

    try:
        with engine.begin() as conn:
            df[['product_id', 'competitor_id', 'price', 'in_stock', 'observed_at']].to_sql(
                "competitor_price",
                conn,
                if_exists="append",
                index=False
            )
        logger.info("Successfully upserted records.")
    except SQLAlchemyError as e:
        logger.error(f"Database error during upsert: {e}")
        raise


@flow(name="Competitor Price Scraping Flow")
def scrape_competitors_flow():
    """
    The main flow to orchestrate the scraping and data loading process.
    """
    products = get_products_to_scrape()
    all_results = []

    # This loop could be parallelized with .map in a real Prefect setup
    for product in products:
        for competitor in COMPETITOR_CONFIG.keys():
            # In Prefect 2, sub-flows are the recommended way for dynamic tasks.
            # For simplicity here, we call the task directly.
            scraped_records = fetch_prices_for_product(product, competitor)
            if scraped_records:
                all_results.extend(scraped_records)

    upsert_prices(all_results)


if __name__ == "__main__":
    # This allows running the flow directly for development and testing.
    # You would typically deploy this to a Prefect server.
    scrape_competitors_flow()
