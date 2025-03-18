# Basic Scraper with Predefined Search URL
# This script extracts product details from Amazon search results using CSS selectors.
# The search term is hardcoded in the URL, making it static.

from crawl4ai import AsyncWebCrawler  # Asynchronous web crawler for scraping web pages
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy  # Strategy to extract data using CSS selectors
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig  # Configuration for browser and crawler
import json  # To parse extracted data into structured format


async def extract_amazon_products():
    """
    Function to scrape Amazon search results using a predefined search URL.
    It extracts details such as title, price, rating, ASIN, and more.
    """

    # Browser Configuration:
    # - browser_type="chromium": Uses Chromium-based browser for scraping.
    # - headless=True: Runs in headless mode (without UI), making it efficient.
    browser_config = BrowserConfig(browser_type="chromium", headless=True)

    # Crawler Configuration:
    # - Uses JSON CSS Extraction Strategy to convert the scraped data into structured JSON.
    crawler_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Amazon Product Search Results",  # Name of the extracted data set
                "baseSelector": "[data-component-type='s-search-result']",  # Identifies individual product listings
                "fields": [
                    {
                        "name": "asin",  # Amazon Standard Identification Number (ASIN)
                        "selector": "",
                        "type": "attribute",
                        # Extracts ASIN from 'data-asin' attribute
                    },
                    {
                        "name": "title",
                        "selector": "h2[aria-label]",
                        "type": "attribute",
                        "attribute": "aria-label",  # Extracts the full title from the aria-label attribute
                    },
                    {
                        "name": "url",  # Product URL
                        "selector": "h2 a",
                        "type": "attribute",
                        "attribute": "href",  # Extracts 'href' attribute from <a> tag
                    },
                    {
                        "name": "image",  # Product image URL
                        "selector": ".s-image",  # Selects <img> with class 's-image'
                        "type": "attribute",
                        "attribute": "src",  # Extracts 'src' attribute of the image
                    },
                    {
                        "name": "rating",  # Customer rating
                        # Extracts rating text
                        "type": "text",
                    },
                    {
                        "name": "reviews_count",
                        "selector": "[data-csa-c-func-deps='aui-da-a-popover'] ~ span span",
                        "type": "text",
                    },
                    {
                        "name": "price",
                        "selector": ".a-price-whole",
                        "type": "text",
                    },
                    {
                        "name": "original_price",
                        "selector": "span[aria-hidden='true']",
                        "type": "text",
                    },
                    {
                        "name": "sponsored",  # Identifies if a product is sponsored
                        "selector": ".puis-sponsored-label-text",
                        "type": "exists",  # Returns True if the selector is found
                    },
                    {
                        "name": "delivery_info",  # Delivery information
                        "selector": "[data-cy='delivery-recipe'] .a-color-base",
                        "type": "text",
                        "multiple": True,  # Extracts multiple text elements (if available)
                    },
                ],
            }
        )
    )

    # Amazon search results page for "Samsung Galaxy Tab".
    # This is a static URL, meaning the search query is fixed.
    url = "https://www.amazon.com/s?k=Samsung+Galaxy+Tab"

    # Using an async context manager ensures proper browser resource handling.
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Initiates the scraping process for the given URL
        result = await crawler.arun(url=url, config=crawler_config)

        # Processing and displaying the extracted data
        if result and result.extracted_content:
            # Convert JSON string output to a Python list of dictionaries
            products = json.loads(result.extracted_content)

            # Loop through each extracted product and display details
            for product in products:
                print("\nProduct Details:")
                print(f"ASIN: {product.get('asin')}")  # Amazon ASIN
                print(f"Title: {product.get('title')}")  # Product title
                print(f"Price: {product.get('price')}")  # Current price
                print(f"Original Price: {product.get('original_price')}")  # Original price before discount
                print(f"Rating: {product.get('rating')}")  # Customer rating
                print(f"Reviews: {product.get('reviews_count')}")  # Number of reviews
                print(f"Sponsored: {'Yes' if product.get('sponsored') else 'No'}")  # Identifies sponsored products
                if product.get("delivery_info"):
                    print(f"Delivery: {' '.join(product['delivery_info'])}")  # Delivery details (if available)
                print("-" * 80)  # Separator for readability


# The script is executed only if run as the main module.
if __name__ == "__main__":
    import asyncio  # Import asyncio for running the asynchronous function

    asyncio.run(extract_amazon_products())  # Run the async function to start scraping

