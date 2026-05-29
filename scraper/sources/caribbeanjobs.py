import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error


def scrape() -> list[dict]:
    """Scrapes job listings from CaribbeanJobs.com filtered to Jamaica."""
    log_scraper_start("caribbeanjobs")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://www.caribbeanjobs.com/SearchResults.aspx?Keywords=&Location=131&Recruiter=All&DisciplineId=0&AltDisciplineId=0&JobType=All&OrderBy=1"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        polite_delay(extra=1.0)

        try:
            response = requests.get(url, headers=headers, timeout=30)
        except Exception as e:
            log_scraper_error("caribbeanjobs", e)
            log_scraper_done("caribbeanjobs", found, inserted, skipped)
            return []

        if response.status_code != 200:
            # If blocked by bot protections, fail gracefully
            log_scraper_error(
                "caribbeanjobs",
                Exception(f"Failed to fetch CaribbeanJobs page, status code: {response.status_code}"),
            )
            log_scraper_done("caribbeanjobs", found, inserted, skipped)
            return []

        blocked_markers = [
            "captcha",
            "access denied",
            "unusual traffic",
            "please verify",
            "robot",
        ]
        lowered = (response.text or "").lower()

        # Block/empty heuristics
        if not response.text or len(response.text) < 500 or any(m in lowered for m in blocked_markers):
            log_scraper_error("caribbeanjobs", Exception("CaribbeanJobs returned empty/blocked response"))
            log_scraper_done("caribbeanjobs", found, inserted, skipped)
            return []
            
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

                requirements_text = description

                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    requirements=requirements_text,
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
