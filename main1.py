#Hook-Based Dynamic Search
# Hooks (after_goto): Executes custom logic after navigating to the URL.
# Search Interaction: Uses Playwright to fill in the search box and click the button.
# Dynamic Loading: Waits for results to load before scraping.
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json
from playwright.async_api import Page, BrowserContext

async def extract_amazon_products():
    # Initialize browser config
    browser_config = BrowserConfig(
        # Sets the browser to run in headless mode (no visible UI)
        headless=True
    )

    # Initialize crawler config with JSON CSS extraction strategy
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Bypasses cache to always fetch fresh content
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Amazon Product Search Results",  # Name of the extracted data set
                "baseSelector": "[data-component-type='s-search-result']",  # Identifies individual product listings
                "fields": [
                    {
                        "name": "asin",  # Amazon Standard Identification Number (ASIN)
                        "selector": "",
                        "type": "attribute",
                        "attribute": "data-asin",  # Extracts ASIN from 'data-asin' attribute
                    },
                    {
                        "name": "title",  # Product title
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
                        "selector": ".s-image",
                        "type": "attribute",
                        "attribute": "src",  # Extracts 'src' attribute of the image
                    },
                    {
                        "name": "rating",  # Customer rating
                        "selector": ".a-icon-star-small .a-icon-alt",  # Selector for rating text
                        "type": "text",
                    },
                    {
                        "name": "reviews_count",  # Number of reviews
                        "selector": "[data-csa-c-func-deps='aui-da-a-popover'] ~ span span",
                        "type": "text",
                    },
                    {
                        "name": "price",  # Current product price
                        "selector": ".a-price-whole",
                        "type": "text",
                    },
                    {
                        "name": "original_price",  # Original (crossed-out) price, if available
                        "selector": "span[aria-hidden='true']",
                        "type": "text",
                    },
                    {
                        "name": "sponsored",  # Whether the product is marked as sponsored
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
        ),
    )

    # URL for Amazon homepage — the crawler will navigate from here
    url = "https://www.amazon.com/"

    async def after_goto(page: Page, context: BrowserContext, url: str, response: dict, **kwargs):
        """Hook called after navigating to each URL — used to perform search actions."""
        print(f"[HOOK] after_goto - Successfully loaded: {url}")

        try:
            # Wait for search box to be available
            search_box = await page.wait_for_selector("#twotabsearchtextbox", timeout=1000)

            # Type the search query
            await search_box.fill("Samsung Galaxy Tab")

            # Wait for the search button to be available
            search_button = await page.wait_for_selector("#nav-search-submit-button", timeout=1000)

            # Click the search button and wait for navigation
            await search_button.click()

            # Wait for the search results to load
            await page.wait_for_selector('[data-component-type="s-search-result"]', timeout=10000)
            print("[HOOK] Search completed and results loaded!")

        except Exception as e:
            # Handle any errors that occur during the search interaction
            print(f"[HOOK] Error during search operation: {str(e)}")

        return page

    # Use context manager for proper resource handling
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Register the after_goto hook to perform the search action
        crawler.crawler_strategy.set_hook("after_goto", after_goto)

        # Start the extraction process
        result = await crawler.arun(url=url, config=crawler_config)

        # Process and print the results
        if result and result.extracted_content:
            # Parse the JSON string into a list of products
            products = json.loads(result.extracted_content)

            # Loop through each extracted product and print its details
            for product in products:
                print("\nProduct Details:")
                print(f"ASIN: {product.get('asin')}")
                print(f"Title: {product.get('title')}")
                print(f"Price: {product.get('price')}")
                print(f"Original Price: {product.get('original_price')}")
                print(f"Rating: {product.get('rating')}")
                print(f"Reviews: {product.get('reviews_count')}")
                print(f"Sponsored: {'Yes' if product.get('sponsored') else 'No'}")
                if product.get("delivery_info"):
                    # Join multiple delivery info lines, if present
                    print(f"Delivery: {' '.join(product['delivery_info'])}")
                print("-" * 80)

if __name__ == "__main__":
    import asyncio

    # Run the async function to start scraping
    asyncio.run(extract_amazon_products())
