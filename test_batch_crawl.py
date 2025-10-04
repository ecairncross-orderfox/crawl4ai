#!/usr/bin/env python3
"""
Test script for Crawl4AI batch crawling functionality
"""
import asyncio
import time
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig

async def test_batch_crawling():
    """Test batch crawling with multiple URLs"""
    print("🕷️  Testing Crawl4AI Batch Crawling")
    print("=" * 50)
    
    # Test URLs
    test_urls = [
        "https://httpbin.org/json",
        "https://httpbin.org/html", 
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers",
        "https://httpbin.org/get"
    ]
    
    print(f"📋 Testing with {len(test_urls)} URLs:")
    for i, url in enumerate(test_urls, 1):
        print(f"  {i}. {url}")
    
    # Configure crawler for batch processing
    browser_config = BrowserConfig(
        headless=True,
        verbose=True
    )
    
    crawler_config = CrawlerRunConfig(
        cache_mode="write_only",
        markdown_generator=None  # Use default
    )
    
    start_time = time.time()
    
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            print(f"\n🚀 Starting batch crawl at {time.strftime('%H:%M:%S')}")
            
            # Use arun_many for batch processing
            results = await crawler.arun_many(
                urls=test_urls,
                config=crawler_config
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"\n✅ Batch crawl completed in {duration:.2f} seconds")
            print(f"📊 Results summary:")
            print(f"   • Total URLs: {len(test_urls)}")
            print(f"   • Successful: {sum(1 for r in results if r.success)}")
            print(f"   • Failed: {sum(1 for r in results if not r.success)}")
            print(f"   • Average time per URL: {duration/len(test_urls):.2f}s")
            
            # Show detailed results
            print(f"\n📄 Detailed Results:")
            print("-" * 70)
            for i, result in enumerate(results, 1):
                status = "✅ SUCCESS" if result.success else "❌ FAILED"
                url_short = result.url.replace("https://httpbin.org/", "")
                content_len = len(result.markdown.raw_markdown) if result.markdown else 0
                
                print(f"{i}. {status} | {url_short:<15} | Content: {content_len:>5} chars")
                
                if not result.success and result.error_message:
                    print(f"   Error: {result.error_message}")
                    
                # Show first 100 chars of content for successful crawls
                if result.success and result.markdown:
                    preview = result.markdown.raw_markdown[:100].replace('\n', ' ')
                    if len(result.markdown.raw_markdown) > 100:
                        preview += "..."
                    print(f"   Preview: {preview}")
                
                print()
            
    except Exception as e:
        print(f"❌ Error during batch crawling: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_batch_crawling())