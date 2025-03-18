#JavaScript Execution for Search
#JavaScript Injection: Executes custom JS in the browser.
# Wait for Selector: Ensures the results are loaded before scraping.
# Simplified Flow: No need for hooks — JavaScript handles everything.
from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json

async def extract_amazon_products():
    # Initialize browser configuration
    browser_config = BrowserConfig(
        headless=True  # Runs the browser in headless mode (no visible UI)
    )

    # JavaScript code to perform the search directly in the browser
    js_code_to_search = """
        (async () => {
            // Fill in the search box with the desired query
            document.querySelector('#twotabsearchtextbox').value = 'Samsung Galaxy Tab';
            // Click the search button to initiate the search
            document.querySelector('#nav-search-submit-button').click();
        })();
    """

    # Configure the crawler with the extraction strategy and JavaScript execution
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Bypass cache to always fetch fresh data
        js_code=js_code_to_search,  # Inject and run the JavaScript for the search
        wait_for='css:[data-component-type="s-search-result"]',  # Wait until product results are loaded
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Amazon Product Search Results",  # Name for the extracted data set
                "baseSelector": "[data-component-type='s-search-result']",  # Selector for each product card
                "fields": [  # Define the fields to extract
                    {
                        "name": "asin",  # Amazon Standard Identification Number (ASIN)
                        "selector": "",
                        "type": "attribute",
                        "attribute": "data-asin",  # Extracts ASIN from the 'data-asin' attribute
                    },
                    {
                        "name": "title",  # Product title
                        "selector": "h2[aria-label]",
                        "type": "attribute",
                        "attribute": "aria-label",  # Extracts the title from 'aria-label'
                    },
                    {
                        "name": "url",  # Product URL
                        "selector": "h2 a",
                        "type": "attribute",
                        "attribute": "href",  # Extracts the 'href' attribute of the anchor tag
                    },
                    {
                        "name": "image",  # Product image URL
                        "selector": ".s-image",
                        "type": "attribute",
                        "attribute": "src",  # Extracts the image URL from the 'src' attribute
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
                        "name": "original_price",  # Original price (if available)
                        "selector": "span[aria-hidden='true']",  
                        "type": "text",
                    },
                    {
                        "name": "sponsored",  # Whether the product is marked as sponsored
                        "selector": ".puis-sponsored-label-text",
                        "type": "exists",  # Returns True if the element is found
                    },
                    {
                        "name": "delivery_info",  # Delivery information
                        "selector": "[data-cy='delivery-recipe'] .a-color-base",
                        "type": "text",
                        "multiple": True,  # Extracts multiple elements if present
                    },
                ],
            }
        ),
    )

    # The starting URL for Amazon
    url = "https://www.amazon.com/"

    # Use a context manager to handle the crawler lifecycle
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Run the crawler and extract the data
        result = await crawler.arun(url=url, config=crawler_config)

        # Process and print the extracted results
        if result and result.extracted_content:
            # Parse the extracted JSON content
            products = json.loads(result.extracted_content)

            # Loop through each product and print its details
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
                    # Join multiple delivery details into a single string
                    print(f"Delivery: {' '.join(product['delivery_info'])}")
                print("-" * 80)

if __name__ == "__main__":
    import asyncio

    # Run the asynchronous function to start scraping
    asyncio.run(extract_amazon_products())
