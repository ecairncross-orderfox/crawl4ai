import requests
import xml.etree.ElementTree as ET
import gzip
import io
import json


def fetch(url: str, timeout: int = 15) -> bytes:
    r = requests.get(url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.content


def parse_sitemap_xml(content: bytes) -> dict:
    root = ET.fromstring(content)
    # strip namespace
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]
    urls = []
    sitemaps = []
    if root.tag == 'urlset':
        for u in root.findall('.//url'):
            loc = u.findtext('loc')
            if loc:
                urls.append(loc.strip())
    elif root.tag == 'sitemapindex':
        for sm in root.findall('.//sitemap'):
            loc = sm.findtext('loc')
            if loc:
                sitemaps.append(loc.strip())
    return {'urls': urls, 'sitemaps': sitemaps}


def discover_sitemaps(domain: str) -> list[str]:
    roots = [f"https://{domain}"]
    if not domain.startswith('www.'):
        roots.append(f"https://www.{domain}")
    sm_candidates = []
    for base in roots:
        sm_candidates.append(base + '/sitemap.xml')
        sm_candidates.append(base + '/sitemap_index.xml')
        # robots.txt
        try:
            robots = fetch(base + '/robots.txt').decode('utf-8', 'replace')
            for line in robots.splitlines():
                if line.lower().startswith('sitemap:'):
                    sm_candidates.append(line.split(':', 1)[1].strip())
        except Exception:
            pass
    # de-dup
    seen = set()
    out = []
    for c in sm_candidates:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def collect_urls_from_sitemaps(sitemaps: list[str], limit: int = 1000) -> list[str]:
    urls = []
    seen = set()
    stack = list(sitemaps)
    while stack and len(urls) < limit:
        sm = stack.pop()
        try:
            content = fetch(sm)
            if sm.endswith('.gz'):
                content = gzip.decompress(content)
            parsed = parse_sitemap_xml(content)
            for u in parsed['urls']:
                if u not in seen:
                    seen.add(u)
                    urls.append(u)
                    if len(urls) >= limit:
                        break
            for sub in parsed['sitemaps']:
                if sub not in seen:
                    seen.add(sub)
                    stack.append(sub)
        except Exception:
            continue
    return urls


def main():
    domain = 'dmgmori.com'
    sitemaps = discover_sitemaps(domain)
    urls = collect_urls_from_sitemaps(sitemaps, limit=1000)
    print(f'count={len(urls)}')
    for u in urls[:30]:
        print(u)
    with open('dmgmori_urls.json', 'w', encoding='utf-8') as f:
        json.dump({'domain': domain, 'count': len(urls), 'urls': urls}, f, indent=2)


if __name__ == '__main__':
    main()





