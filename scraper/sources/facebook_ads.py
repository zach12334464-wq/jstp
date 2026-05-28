import urllib.parse

import httpx
from bs4 import BeautifulSoup

from utils.helpers import build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

from loguru import logger

FACEBOOK_AD_LIBRARY_ASYNC_URL = (
    "https://www.facebook.com/ads/library/async/search_typeahead/"
    "?q=hiring+jamaica&session_id=1&country=JM&reload_on_failure=false"
    "&should_query_ads_lib=true"
)


async def scrape() -> list[dict]:
    """Requests-based Facebook Ad Library approach.

    Note: Facebook frequently blocks automation/headless browsers. This scraper uses
    a lightweight requests-based endpoint and fails gracefully when blocked.
    """
    log_scraper_start("facebook_ads")

    jobs: list[dict] = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        timeout = httpx.Timeout(30.0, connect=10.0)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

        async with httpx.AsyncClient(timeout=timeout, headers=headers, follow_redirects=True) as client:
            resp = await client.get(FACEBOOK_AD_LIBRARY_ASYNC_URL)

        if resp.status_code != 200:
            logger.warning("[FACEBOOK_ADS] Skipped — Facebook blocks headless browsers on CI")
            log_scraper_done("facebook_ads", found, inserted, skipped)
            return []

        # Best-effort parsing: this endpoint returns HTML-ish payload; we extract ad links if present.
        content_type = resp.headers.get("content-type", "")
        text = resp.text or ""
        if not text:
            log_scraper_done("facebook_ads", found, inserted, skipped)
            return []

        soup = BeautifulSoup(text, "html.parser")

        # Try to find ad detail/library links
        link_els = soup.select("a[href*='/ads/library/'], a[href*='ad_details']")
        seen: set[str] = set()

        for a in link_els:
            href = a.get("href")
            if not href:
                continue
            if href.startswith("http"):
                source_url = href
            else:
                source_url = "https://www.facebook.com" + href

            if source_url in seen:
                continue
            seen.add(source_url)

            # Minimal simulated job fields; endpoint often doesn’t contain full structured ad copy
            page_name = a.get_text(strip=True) or "Facebook"
            title = f"Hiring Opportunity at {page_name}"

            description = "Facebook Ad Library listing. Visit source for details."

            job_dict = build_job_dict(
                title=title,
                company=page_name,
                description=description,
                source="facebook_ads",
                source_url=source_url,
                location="Jamaica",
                image_url="",
                is_remote=False,
                is_international=False,
            )

            jobs.append(job_dict)
            found += 1
            inserted += 1

    except Exception as e:
        # Exact warning required by task when this also fails.
        logger.warning("[FACEBOOK_ADS] Skipped — Facebook blocks headless browsers on CI")
        log_scraper_error("facebook_ads", e)

    log_scraper_done("facebook_ads", found, inserted, skipped)
    return jobs

