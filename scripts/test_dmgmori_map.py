import asyncio
import json
import os
import sys

# Ensure local package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from crawl4ai.url_map import map_site


async def main():
    domain = "dmgmori.com"
    urls = await map_site(domain, limit=200, source="sitemap")
    data = {
        "domain": domain,
        "count": len(urls),
        "sample": urls[:50],
    }
    with open("dmgmori_urls.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    # Also print short summary
    print(f"count={len(urls)}")
    for u in urls[:20]:
        print(u)


if __name__ == "__main__":
    asyncio.run(main())


