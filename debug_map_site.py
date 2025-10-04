#!/usr/bin/env python3
import asyncio
import json
import sys
import os
import traceback

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

try:
    from crawl4ai.url_map import map_site
    print("✓ Successfully imported map_site")
except Exception as e:
    print(f"✗ Failed to import map_site: {e}")
    traceback.print_exc()
    sys.exit(1)

async def main():
    try:
        print("Testing map_site function...")
        domain = "dmgmori.com"
        print(f"Calling map_site('{domain}', limit=200, source='sitemap')")

        urls = await map_site(domain, limit=200, source="sitemap")
        print(f"✓ map_site completed successfully")
        print(f"Found {len(urls)} URLs")

        if urls:
            print("First 10 URLs:")
            for i, url in enumerate(urls[:10]):
                print(f"  {i+1}. {url}")
        else:
            print("No URLs found - this indicates a potential issue")

        # Try with different source
        print(f"\nTrying with source='sitemap+cc'...")
        urls2 = await map_site(domain, limit=200, source="sitemap+cc")
        print(f"Found {len(urls2)} URLs with sitemap+cc")

        return urls

    except Exception as e:
        print(f"✗ Error in map_site: {e}")
        traceback.print_exc()
        return []

if __name__ == "__main__":
    results = asyncio.run(main())
    print(f"\nFinal result: {len(results)} URLs")