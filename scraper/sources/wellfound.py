from playwright.sync_api import sync_playwright
from utils.helpers import polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

from loguru import logger

def scrape() -> list[dict]:
    """Scrapes remote internships and entry-level listings from Wellfound (AngelList Talent)."""
    log_scraper_start("wellfound")
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

        url = "https://wellfound.com/jobs?remote=true&role=internship"
        
        # Respectful polite delay
        polite_delay(extra=1.0)
        
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Let dynamic React scripts load job grids
        page.wait_for_timeout(4000)
        
        # Wellfound cards typically have test-ids or component classes
        cards = page.query_selector_all("div[class*='jobCard'], div[data-testid='JobCard'], div[class*='styles_jobCard']")
        
        if not cards:
            # Fallback to broad list element queries
            cards = page.query_selector_all("div[class*='styles_component__'], div[class*='styles_result__'], div[class*='styles_card__']")

        logger.info(f"[WELLFOUND] Found {len(cards)} potential job card elements")

        for card in cards:
            try:
                # 1. Title & Link
                title = ""
                title_el = card.query_selector("h3") or card.query_selector("h4") or card.query_selector("div[class*='title']")
                if title_el:
                    title = title_el.inner_text()
                    
                link_el = card.query_selector("a[href*='/jobs/'], a[href*='/l/jobs/']")
                source_url = ""
                if link_el:
                    source_url = link_el.get_attribute("href")
                    if not title and not source_url.endswith("/jobs"):
                        title = link_el.inner_text()
                        
                if not source_url:
                    continue
                    
                if not source_url.startswith("http"):
                    source_url = "https://wellfound.com" + source_url
                    
                # Deduplicate in run
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                if not title:
                    title = "Remote Startup Internship"
                    
                # 2. Company Name
                company = ""
                company_el = card.query_selector("h2") or card.query_selector("span[class*='company'], a[class*='companyName']")
                if company_el:
                    company = company_el.inner_text()
                if not company:
                    # Look for links pointing to startup profiles
                    startup_link = card.query_selector("a[href*='/company/']")
                    if startup_link:
                        company = startup_link.inner_text()
                if not company:
                    company = "Wellfound Startup"
                    
                # 3. Description Snippet
                description = ""
                desc_el = card.query_selector("div[class*='description'], p[class*='description'], div[class*='snippet']")
                if desc_el:
                    description = desc_el.inner_text()
                if not description:
                    description = f"Remote internship opportunity for {title} at {company} on Wellfound. Explore startup life and gain hands-on industry experience."
                    
                # 4. Salary / Equity information
                salary = ""
                salary_el = card.query_selector("span[class*='salary'], div[class*='salary'], span[class*='compensation']")
                if salary_el:
                    salary = salary_el.inner_text()
                else:
                    for line in card.inner_text().split("\n"):
                        if "$" in line or "equity" in line.lower() or "€" in line:
                            salary = line
                            break
                            
                # 5. Startup Logo URL
                image_url = ""
                img_el = card.query_selector("img[class*='logo'], img[class*='Logo'], img")
                if img_el:
                    src = img_el.get_attribute("src")
                    if src and src.startswith("http"):
                        image_url = src
                        
                found += 1
                
                requirements_text = description

                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    requirements=requirements_text,
                    source="wellfound",
                    source_url=source_url,
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

        log_scraper_done("wellfound", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("wellfound", e)
        log_scraper_done("wellfound", found, inserted, skipped)
        
    finally:
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
            
    return jobs
