import asyncio
import json
import os
import importlib.util


def _load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[arg-type]
    return mod


async def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    seeder_path = os.path.join(repo_root, "crawl4ai", "async_url_seeder.py")
    configs_path = os.path.join(repo_root, "crawl4ai", "async_configs.py")

    c4a_seeder = _load_module("c4a_seeder", seeder_path)
    c4a_configs = _load_module("c4a_configs", configs_path)

    AsyncUrlSeeder = getattr(c4a_seeder, "AsyncUrlSeeder")
    SeedingConfig = getattr(c4a_configs, "SeedingConfig")

    roots = ["dmgmori.com", "www.dmgmori.com"]
    cfg = SeedingConfig(
        source="sitemap+cc",
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

    seen = set()
    urls = []
    for u in all_urls:
        if u not in seen:
            seen.add(u)
            urls.append(u)

    print(f"count={len(urls)}")
    for u in urls[:30]:
        print(u)

    out = {"domains": roots, "count": len(urls), "urls": urls}
    with open("dmgmori_urls.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())





