from playwright.sync_api import sync_playwright
from utils.helpers import polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

from loguru import logger

def scrape() -> list[dict]:
    """Scrapes independent freelance opportunities from Contra using synchronous Playwright."""
    log_scraper_start("contra")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    playwright = None
    browser = None
    
    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        url = "https://contra.com/opportunities"
        
        # Respectful polite delay
        polite_delay(extra=1.0)
        
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Let dynamic React scripts render opportunities
        page.wait_for_timeout(4000)
        
        # Contra's opportunity cards can be queried by link href patterns or custom class attributes
        cards = page.query_selector_all("a[href*='/opportunity/']") or page.query_selector_all("div[class*='OpportunityCard']")
        
        if not cards:
            # Fallback to general cards
            cards = page.query_selector_all("div[class*='Card'], div[class*='card'], article")

        logger.info(f"[CONTRA] Found {len(cards)} potential opportunity elements")

        for card in cards:
            try:
                # 1. Link / Source URL
                link_href = ""
                if card.name == 'a':
                    link_href = card.get_attribute("href")
                else:
                    link_el = card.query_selector("a[href*='/opportunity/']") or card.query_selector("a")
                    if link_el:
                        link_href = link_el.get_attribute("href")
                        
                if not link_href:
                    continue
                    
                if not link_href.startswith("http"):
                    link_href = "https://contra.com" + link_href
                    
                # Deduplicate in run
                if any(j["source_url"] == link_href for j in jobs):
                    continue

                # 2. Title
                title = ""
                title_el = card.query_selector("h2") or card.query_selector("h3") or card.query_selector("div[class*='title']")
                if title_el:
                    title = title_el.inner_text()
                if not title:
                    # Parse card text
                    text_lines = card.inner_text().split("\n")
                    if text_lines:
                        title = text_lines[0]
                if not title or len(title) > 100:
                    title = "Freelance Project Opportunity"
                
                # 3. Client / Company Name
                client = ""
                client_el = card.query_selector("span[class*='client'], div[class*='client'], span[class*='Name']")
                if client_el:
                    client = client_el.inner_text()
                if not client:
                    # Sift for text that looks like a username or profile
                    text_lines = card.inner_text().split("\n")
                    if len(text_lines) > 1:
                        client = text_lines[1]
                if not client or len(client) > 50:
                    client = "Contra Client"
                    
                # 4. Description
                description = ""
                desc_el = card.query_selector("div[class*='description'], p[class*='description'], div[class*='body']")
                if desc_el:
                    description = desc_el.inner_text()
                if not description:
                    description = f"Freelance project contract for {title} on Contra. Work with {client} remotely. See details on Contra."
                
                # 5. Salary / Budget Rate
                salary = ""
                salary_el = card.query_selector("span[class*='budget'], div[class*='rate'], span[class*='rate']")
                if salary_el:
                    salary = salary_el.inner_text()
                else:
                    # search text lines for dollar sign
                    for line in card.inner_text().split("\n"):
                        if "$" in line or "USD" in line:
                            salary = line
                            break
                            
                # 6. Avatar/Logo
                image_url = ""
                img_el = card.query_selector("img[class*='avatar'], img[class*='Avatar'], img")
                if img_el:
                    src = img_el.get_attribute("src")
                    if src and src.startswith("http"):
                        image_url = src
                
                found += 1
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=client,
                    description=description,
                    source="contra",
                    source_url=link_href,
                    location="Remote — Work from Anywhere",
                    image_url=image_url,
                    salary=salary,
                    is_remote=True,
                    is_international=True,
                    payment_methods=["PayPal", "Wise", "Payoneer"]
                )
                
                # Override parish to Jamaica as required
                job_dict["parish"] = "Jamaica"
                
                jobs.append(job_dict)
                inserted += 1
                
            except Exception as card_err:
                skipped += 1
                continue

        log_scraper_done("contra", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("contra", e)
        log_scraper_done("contra", found, inserted, skipped)
        
    finally:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
            
    return jobs
