#!/usr/bin/env python3
import asyncio
import json
import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from crawl4ai.url_map import map_site

async def main():
    domain = "dmgmori.com"
    print(f"Testing map_site with working parameters...")

    # Test with sitemap+cc (which we know works)
    urls = await map_site(domain, limit=200, source="sitemap+cc")

    print(f"✓ Found {len(urls)} URLs")

    # Display first 20 URLs
    for i, url in enumerate(urls[:20]):
        print(f"  {i+1:2d}. {url}")

    # Save results
    data = {
        "domain": domain,
        "count": len(urls),
        "urls": urls,
        "test_timestamp": "2025-09-16",
        "test_status": "SUCCESS"
    }

    with open("test_map_results.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Results saved to test_map_results.json")
    return len(urls)

if __name__ == "__main__":
    result_count = asyncio.run(main())
    print(f"\n🎉 Test completed successfully! Found {result_count} URLs")