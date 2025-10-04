from __future__ import annotations

from typing import List, Optional

from .async_url_seeder import AsyncUrlSeeder
from .async_configs import SeedingConfig


async def map_site(
    root: str,
    limit: int = 1000,
    *,
    source: str = "sitemap+cc",
    pattern: str = "*",
    extract_head: bool = False,
    live_check: bool = False,
    concurrency: int = 200,
    hits_per_sec: int = 5,
    query: Optional[str] = None,
    score_threshold: Optional[float] = None,
    filter_nonsense_urls: bool = True,
) -> List[str]:
    """Discover up to `limit` URLs starting from `root` using Crawl4AI's URL Seeder.

    Returns a flat list of absolute URLs. Configure discovery via sitemaps and Common Crawl,
    optionally enabling head extraction + BM25 scoring with a query.
    """
    cfg = SeedingConfig(
        source=source,
        pattern=pattern,
        extract_head=extract_head,
        live_check=live_check,
        max_urls=limit,
        concurrency=concurrency,
        hits_per_sec=hits_per_sec,
        query=query,
        score_threshold=score_threshold,
        filter_nonsense_urls=filter_nonsense_urls,
    )

    async with AsyncUrlSeeder() as seeder:
        results = await seeder.urls(root, cfg)

    return [r["url"] for r in results]






