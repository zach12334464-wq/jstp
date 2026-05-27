import requests
from datetime import datetime
from config import REMOTE_BLOCKLIST
from utils.helpers import polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error


def scrape() -> list[dict]:
    """Scrapes remote job listings from Remotive API."""
    log_scraper_start("remotive")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://remotive.com/api/remote-jobs?category=other&limit=50"
        headers = {
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        polite_delay(extra=1.0)
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch Remotive API, status code: {response.status_code}")
            
        data = response.json()
        job_listings = data.get("jobs", [])

        for job in job_listings:
            try:
                title = job.get("title", "")
                company = job.get("company_name", "")
                description = job.get("description", "")
                source_url = job.get("url", "")
                salary = job.get("salary", "")
                image_url = job.get("company_logo", "")
                
                # Check candidate_required_location restriction
                required_location = job.get("candidate_required_location", "").lower()
                
                # Filter out jobs that are restricted to specific regions outside Jamaica / global remote
                is_blocked = False
                if required_location:
                    for block_term in REMOTE_BLOCKLIST:
                        if block_term in required_location:
                            is_blocked = True
                            break
                            
                if is_blocked:
                    skipped += 1
                    continue

                found += 1
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    source="remotive",
                    source_url=source_url,
                    location="Remote — Work from Anywhere",
                    image_url=image_url,
                    salary=salary,
                    is_remote=True,
                    is_international=True
                )
                
                # Override parish to Jamaica as required
                job_dict["parish"] = "Jamaica"
                
                jobs.append(job_dict)
                inserted += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("remotive", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("remotive", e)
        log_scraper_done("remotive", found, inserted, skipped)
        
    return jobs
