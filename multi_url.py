import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode

async def quick_parallel_example():
    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]

    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=True  # Enable streaming mode
    )

    async with AsyncWebCrawler() as crawler:
        # Stream results as they complete
        async for result in await crawler.arun_many(urls, config=run_conf):
            if result.success:
                print(f"[OK] {result.url}, length: {len(result.markdown.raw_markdown)}")
            else:
                print(f"[ERROR] {result.url} => {result.error_message}")

        # Or get all results at once (default behavior)
        run_conf = run_conf.clone(stream=False)
        results = await crawler.arun_many(urls, config=run_conf)
        for res in results:
            if res.success:
                print(f"[OK] {res.url}, length: {len(res.markdown.raw_markdown)}")
            else:
                print(f"[ERROR] {res.url} => {res.error_message}")

if __name__ == "__main__":
    asyncio.run(quick_parallel_example())