import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from scraper.utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

def scrape() -> list[dict]:
    """Scrapes job listings from CaribbeanJobs.com filtered to Jamaica."""
    log_scraper_start("caribbeanjobs")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://www.caribbeanjobs.com/ShowResults.aspx?Keywords=&autosuggest=&Location=Jamaica"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.caribbeanjobs.com/"
        }
        
        polite_delay(extra=1.0)
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch CaribbeanJobs page, status code: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Look for job listing cards or general search result containers
        cards = soup.select("div.job-result") or soup.select(".job-listing") or soup.select("div.search-result")
        
        # Fallback to broad anchor tag matching
        if not cards:
            links = soup.find_all("a", href=lambda h: h and ("/job/" in h or "ShowJob.aspx" in h))
            cards = [link.find_parent("div") or link for link in links]

        for card in cards:
            try:
                # Find link to full description
                link_el = card.find("a", href=True)
                if not link_el:
                    link_el = card if (card.name == 'a' and card.get("href")) else None
                if not link_el:
                    continue
                    
                source_url = link_el["href"]
                if not source_url.startswith("http"):
                    source_url = "https://www.caribbeanjobs.com" + source_url
                    
                # Deduplicate
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Title
                title_el = card.find("h2") or card.find("h3") or card.find(class_="title") or link_el
                title = title_el.get_text().strip() if title_el else "Job Vacancy"
                if title == source_url or not title:
                    title = link_el.get_text().strip()
                if not title:
                    title = "Job Opportunity"
                
                # Company
                company_el = card.find(class_="company") or card.find(class_="job-company") or card.find(class_="employer")
                company = company_el.get_text().strip() if company_el else "CaribbeanJobs Employer"
                
                # Location
                location_el = card.find(class_="location") or card.find(class_="job-location")
                location = location_el.get_text().strip() if location_el else "Jamaica"
                
                # Description
                desc_el = card.find(class_="description") or card.find(class_="job-description") or card.find(class_="summary")
                description = desc_el.get_text().strip() if desc_el else f"Job listing for {title} at {company} in {location}."
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    source="caribbeanjobs",
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
                
        log_scraper_done("caribbeanjobs", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("caribbeanjobs", e)
        log_scraper_done("caribbeanjobs", found, inserted, skipped)
        
    return jobs
