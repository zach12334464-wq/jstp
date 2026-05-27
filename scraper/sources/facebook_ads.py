import asyncio
import urllib.parse
from playwright.async_api import async_playwright
from config import FACEBOOK_AD_SEARCH_TERMS, FACEBOOK_AD_COUNTRY
from utils.helpers import polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

from loguru import logger

async def scrape() -> list[dict]:
    """Scrapes hiring ads from Facebook Ad Library using Playwright (async)."""
    log_scraper_start("facebook_ads")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    playwright = None
    browser = None
    
    try:
        playwright = await async_playwright().start()
        # Launch headless browser for background scraping
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for term in FACEBOOK_AD_SEARCH_TERMS:
            try:
                logger.info(f"[FACEBOOK_ADS] Searching for term: '{term}'")
                
                # Polite delay between terms
                polite_delay(extra=2.0)
                
                encoded_term = urllib.parse.quote(term)
                search_url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={FACEBOOK_AD_COUNTRY}&q={encoded_term}&search_type=keyword_unordered"
                
                await page.goto(search_url, wait_until="networkidle", timeout=30000)
                
                # Let dynamic scripts load
                await page.wait_for_timeout(3000)
                
                # Facebook Ad Library containers are typically card elements
                # Let's search for divs representing ad cards using class name matches or data-testids
                cards = await page.query_selector_all("div[class*='_7jvw'], div[class*='_2e_b'], div[data-testid='ad_card']")
                
                if not cards:
                    # Generic fallback container selection
                    cards = await page.query_selector_all("div[class*='_9npi'], div[class*='_7jwv']")

                logger.info(f"[FACEBOOK_ADS] Found {len(cards)} ad card elements for '{term}'")

                for card in cards:
                    try:
                        # 1. Page Name (Advertiser Business Name)
                        page_name = ""
                        page_name_el = await card.query_selector("span[class*='_7jwc'], a[class*='_7jwc'], div[class*='_7jwc']")
                        if page_name_el:
                            page_name = await page_name_el.inner_text()
                        
                        if not page_name:
                            # Sift bold tags/anchors
                            anchors = await card.query_selector_all("a")
                            for a in anchors:
                                text = await a.inner_text()
                                if text and len(text) > 2 and "see ad details" not in text.lower():
                                    page_name = text
                                    break
                                    
                        if not page_name:
                            page_name = "Facebook Business"
                            
                        # 2. Ad Text (Copy body)
                        ad_text = ""
                        ad_text_el = await card.query_selector("div[class*='_1o0'], div[class*='_8thz'], div[class*='_8nhi']")
                        if ad_text_el:
                            ad_text = await ad_text_el.inner_text()
                        else:
                            # Search for divs with readable text
                            divs = await card.query_selector_all("div")
                            for d in divs:
                                text = await d.inner_text()
                                if text and len(text) > 40 and "id:" not in text.lower() and "active" not in text.lower():
                                    ad_text = text
                                    break
                                    
                        if not ad_text:
                            continue  # If we can't get any text, discard this card

                        # 3. Image URL
                        image_url = ""
                        img_el = await card.query_selector("img[src*='fbcdn'], img")
                        if img_el:
                            src = await img_el.get_attribute("src")
                            if src and src.startswith("http"):
                                image_url = src
                                
                        # 4. Ad URL (Details Page Link)
                        ad_url = ""
                        ad_url_el = await card.query_selector("a[href*='ad_details'], a[href*='facebook.com/ads/library']")
                        if ad_url_el:
                            href = await ad_url_el.get_attribute("href")
                            if href:
                                ad_url = href
                        
                        if not ad_url:
                            # Construct a general library link fallback
                            ad_url = f"https://www.facebook.com/ads/library/?id={page_name}"

                        # Prevent duplicate insertions
                        if any(j["source_url"] == ad_url for j in jobs):
                            continue

                        found += 1
                        
                        # Build simulated job posting
                        # Title can be derived from advertiser name + term
                        title = f"Hiring Opportunity at {page_name}"
                        
                        job_dict = build_job_dict(
                            title=title,
                            company=page_name,
                            description=ad_text,
                            source="facebook_ads",
                            source_url=ad_url,
                            location="Jamaica",
                            image_url=image_url,
                            is_remote=False,
                            is_international=False
                        )
                        
                        jobs.append(job_dict)
                        inserted += 1
                        
                    except Exception as card_err:
                        skipped += 1
                        continue
                        
            except Exception as term_err:
                logger.error(f"[FACEBOOK_ADS] Error searching for term '{term}': {term_err}")
                continue

        log_scraper_done("facebook_ads", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("facebook_ads", e)
        log_scraper_done("facebook_ads", found, inserted, skipped)
        
    finally:
        # Secure resource cleanup
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
            
    return jobs
