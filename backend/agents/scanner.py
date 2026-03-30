import hashlib
import os
import re
from datetime import datetime

import httpx

from backend.services.bright_data import bright_data


async def scan_marketplace(marketplace: str, region: str, search_queries: list[str]) -> list[dict]:
    parsers = {"olx.th": parse_olx_th, "chotot.com": parse_cho_tot}
    parser = parsers.get(marketplace)
    if not parser:
        raise ValueError(f"No parser for marketplace: {marketplace}")
    country = {"olx.th": "TH", "chotot.com": "VN"}.get(marketplace, "TH")
    all_listings = []
    for query in search_queries:
        url = _build_search_url(marketplace, query)
        html = await bright_data.scrape_as_html(url)
        listings = parser(html, marketplace, region)
        all_listings.extend(listings)
    return all_listings


def parse_olx_th(html: str, marketplace: str, region: str) -> list[dict]:
    listings = []
    title_pattern = re.compile(r'<h[23][^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</h[23]>', re.DOTALL)
    price_pattern = re.compile(r'<span[^>]*class="[^"]*price[^"]*"[^>]*>(.*?)</span>', re.DOTALL)
    image_pattern = re.compile(r'<img[^>]*src="(https?://[^"]+)"[^>]*/>', re.DOTALL)
    link_pattern = re.compile(r'<a[^>]*href="(/item/[^"]+)"[^>]*>', re.DOTALL)
    titles = title_pattern.findall(html)
    prices = price_pattern.findall(html)
    images = image_pattern.findall(html)
    links = link_pattern.findall(html)
    for i, title in enumerate(titles):
        title_clean = re.sub(r'<[^>]+>', '', title).strip()
        price_text = prices[i] if i < len(prices) else ""
        price_clean = re.sub(r'[^\d.]', '', re.sub(r'<[^>]+>', '', price_text))
        listing_id = links[i] if i < len(links) else f"olx-{i}"
        content_hash = hashlib.sha256(f"{title_clean}|{marketplace}|{listing_id}".encode()).hexdigest()
        listings.append({
            "platform_listing_id": listing_id, "title": title_clean, "description": "",
            "price_amount": float(price_clean) if price_clean else None, "price_currency": "THB",
            "images": [images[i]] if i < len(images) else [], "seller_id": None, "seller_name": None,
            "seller_join_date": None, "seller_listing_count": None, "location_text": None,
            "post_date": datetime.utcnow().isoformat(), "platform": marketplace,
            "platform_category": None, "raw_html": html[:5000],
            "content_hash": content_hash, "language": "th",
        })
    return listings


def parse_cho_tot(html: str, marketplace: str, region: str) -> list[dict]:
    return []


async def download_images(listings: list[dict], scan_job_id: str, static_dir: str) -> list[dict]:
    job_dir = os.path.join(static_dir, scan_job_id)
    os.makedirs(job_dir, exist_ok=True)
    async with httpx.AsyncClient(timeout=30.0) as client:
        for listing in listings:
            local_images = []
            for i, img_url in enumerate(listing.get("images", [])):
                try:
                    resp = await client.get(img_url)
                    resp.raise_for_status()
                    ext = img_url.rsplit(".", 1)[-1][:4] if "." in img_url else "jpg"
                    filename = f"{listing['content_hash'][:12]}_{i}.{ext}"
                    filepath = os.path.join(job_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(resp.content)
                    local_images.append(f"/static/images/{scan_job_id}/{filename}")
                except Exception:
                    continue
            listing["images_local"] = local_images
    return listings


def _build_search_url(marketplace: str, query: str) -> str:
    urls = {
        "olx.th": f"https://www.olx.co.th/en/items/q-{query}",
        "chotot.com": f"https://www.chotot.com/mua-ban?q={query}",
    }
    return urls.get(marketplace, "")
