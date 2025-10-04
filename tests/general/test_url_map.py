import asyncio
import pytest

from crawl4ai.url_map import map_site


@pytest.mark.asyncio
async def test_map_site_basic():
    urls = await map_site("https://example.com", limit=10, source="sitemap+cc")
    assert isinstance(urls, list)
    assert all(isinstance(u, str) for u in urls)
    # not asserting non-empty because example.com may not have sitemap or CC hits





