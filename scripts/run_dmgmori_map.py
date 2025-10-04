import asyncio
import json
from crawl4ai.async_url_seeder import AsyncUrlSeeder
from crawl4ai.async_configs import SeedingConfig


async def main():
    roots = ["dmgmori.com", "www.dmgmori.com"]
    cfg = SeedingConfig(
        source="sitemap+cc",   # try sitemaps and Common Crawl
        pattern="*",
        max_urls=1000,
        extract_head=False,
        live_check=False,
        concurrency=200,
        hits_per_sec=5,
    )
    all_urls = []
    async with AsyncUrlSeeder() as seeder:
        for root in roots:
            results = await seeder.urls(root, cfg)
            all_urls.extend([r["url"] for r in results])

    # De-duplicate while preserving order
    seen = set()
    urls = []
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            urls.append(u)

    print(f"count={len(urls)}")
    for u in urls[:20]:
        print(u)

    with open("dmgmori_urls.json", "w", encoding="utf-8") as f:
        json.dump({"domains": roots, "count": len(urls), "urls": urls}, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())


