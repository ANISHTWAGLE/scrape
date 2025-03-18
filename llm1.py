import os
import json
import asyncio
import logging
from typing import Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode
from pydantic import BaseModel, Field
from crawl4ai.extraction_strategy import LLMExtractionStrategy

# Configure logging only for LiteLLM instead of enabling DEBUG globally
logging.getLogger("LiteLLM").setLevel(logging.DEBUG)
logging.getLogger("crawl4ai").setLevel(logging.INFO)  # Keep general logs cleaner

class OpenAIModelFee(BaseModel):
    model_name: str = Field(..., description="Name of the OpenAI model.")
    input_fee: str = Field(..., description="Fee for input token for the OpenAI model.")
    output_fee: str = Field(..., description="Fee for output token for the OpenAI model.")

    @classmethod
    def model_json_schema(cls):
        # Return a more explicit schema for the model (if needed)
        return {
            "type": "object",
            "properties": {
                "model_name": {"type": "string"},
                "input_fee": {"type": "string"},
                "output_fee": {"type": "string"}
            },
            "required": ["model_name", "input_fee", "output_fee"]
        }

async def extract_structured_data_using_llm(provider: str, api_token: str = None):
    print(f"\n--- Extracting Structured Data with {provider} ---")

    browser_config = BrowserConfig(headless=True)

    extraction_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider=provider, api_token=api_token),
        schema=OpenAIModelFee.model_json_schema(),
        extraction_type="schema",
        instruction="""From the crawled content, extract all mentioned model names along with their fees for input and output tokens.
        Provide a structured JSON output with fields: model_name, input_fee, output_fee.
        Ensure that no model or fee is missed and output is formatted properly."""
    )

    print("Extraction strategy initialized")

    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        word_count_threshold=1,
        page_timeout=80000,
        extraction_strategy=extraction_strategy,
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url="https://openai.com/api/pricing/", config=crawler_config)

        # Debug raw response before parsing
        print("\n=== Raw Extracted Content ===\n", result.extracted_content)

        if result.extracted_content:
            try:
                extracted_data = json.loads(result.extracted_content)
                print("\n=== Parsed Extracted Data ===\n", extracted_data)
            except json.JSONDecodeError as e:
                print(f"\n!!! JSON Parsing Error: {e} !!!")
                print("\n--- Check the extracted content manually ---\n")


if __name__ == "__main__":
    asyncio.run(extract_structured_data_using_llm(provider="ollama/llama3.2:1b", api_token=None))
