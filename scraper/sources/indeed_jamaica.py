import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
from config import MAX_RETRIES
from utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

from loguru import logger

def scrape() -> list[dict]:
    """Scrapes job listings from Indeed Jamaica with retries and robust parsing."""
    log_scraper_start("indeed_jamaica")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0
    
    url = "https://jm.indeed.com/jobs?q=internship+OR+part+time+OR+entry+level&l=Jamaica"
    retries = 0
    response = None
    
    while retries < MAX_RETRIES:
        try:
            # Respectful polite delay with extra 2.0s
            polite_delay(extra=2.0)
            
            headers = {
                "User-Agent": get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://jm.indeed.com/"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                html_lower = response.text.lower()
                if "cloudflare" in html_lower or "hcaptcha" in html_lower or "security check" in html_lower or "robot" in html_lower:
                    logger.warning("[INDEED_JAMAICA] Scraper blocked by security challenge / Captcha.")
                    break
                break  # Successful fetch!
            elif response.status_code in [403, 503]:
                logger.warning(f"[INDEED_JAMAICA] Access denied (status code {response.status_code}). Retrying...")
            else:
                logger.warning(f"[INDEED_JAMAICA] Failed request (status code {response.status_code}). Retrying...")
                
        except Exception as e:
            logger.warning(f"[INDEED_JAMAICA] Network or connection error: {e}. Retrying...")
            
        retries += 1
        time.sleep(2 ** retries)  # Exponential backoff
        
    # If blocked, log a warning and return empty list gracefully
    if not response or response.status_code != 200 or "cloudflare" in response.text.lower() or "hcaptcha" in response.text.lower() or "security check" in response.text.lower():
        logger.warning("[INDEED_JAMAICA] Aborted scraper due to blocks or request failures.")
        log_scraper_done("indeed_jamaica", found, inserted, skipped)
        return jobs
        
    try:
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Indeed job card class selectors
        cards = soup.select("div.job_seen_beacon") or soup.select("td.resultContent") or soup.select(".slider_container")
        
        # General backup if specific classes aren't matched
        if not cards:
            cards = soup.find_all("div", class_=lambda c: c and ("job" in c or "result" in c))

        for card in cards:
            try:
                # Extract Title & Link
                title_el = card.find(class_="jcs-JobTitle") or card.find("h2") or card.find("a")
                if not title_el:
                    continue
                    
                title = title_el.get_text().strip()
                
                link_el = title_el if title_el.name == 'a' else title_el.find("a")
                source_url = ""
                if link_el and link_el.get("href"):
                    source_url = link_el["href"]
                else:
                    source_url = title_el.get("href", "")
                    
                if not source_url:
                    continue
                    
                if not source_url.startswith("http"):
                    source_url = "https://jm.indeed.com" + source_url
                    
                # Deduplicate
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Company
                company_el = card.find(class_="companyName") or card.find(class_="css-1xk4156") or card.find("[data-testid='company-name']") or card.find(class_="company")
                company = company_el.get_text().strip() if company_el else "Indeed Employer"
                
                # Location
                location_el = card.find(class_="companyLocation") or card.find(class_="css-6s8afy") or card.find("[data-testid='text-location']") or card.find(class_="location")
                location = location_el.get_text().strip() if location_el else "Jamaica"
                
                # Description Snippet
                desc_el = card.find(class_="jobCardShelfContainer") or card.find(class_="job-snippet") or card.find(class_="summary")
                description = desc_el.get_text().strip() if desc_el else f"Hiring for {title} at {company} in {location}. Visit Indeed Jamaica for details."
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    source="indeed_jamaica",
                    source_url=source_url,
                    location=location,
                    image_url="",
                    is_remote=False,
                    is_international=False
                )
                
                jobs.append(job_dict)
                inserted += 1
                found += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("indeed_jamaica", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("indeed_jamaica", e)
        log_scraper_done("indeed_jamaica", found, inserted, skipped)
        
    return jobs
