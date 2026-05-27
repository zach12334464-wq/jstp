import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error


def scrape() -> list[dict]:
    """Scrapes entry-level remote job listings from Remote.co."""
    log_scraper_start("remote_co")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://remote.co/remote-jobs/entry-level/"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://remote.co/"
        }
        
        polite_delay(extra=1.0)
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch Remote.co, status code: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remote.co listings are structured as anchors with class card or inside card lists
        cards = soup.select("a.card") or soup.select(".card") or soup.select("div.job-card")
        
        if not cards:
            links = soup.find_all("a", href=lambda h: h and "/remote-jobs/" in h)
            cards = [link.find_parent("div") or link for link in links]

        for card in cards:
            try:
                # Find link to the vacancy
                link_el = card if card.name == 'a' else card.find("a", href=True)
                if not link_el or not link_el.get("href"):
                    continue
                    
                source_url = link_el["href"]
                if not source_url.startswith("http"):
                    source_url = "https://remote.co" + source_url
                    
                # Deduplicate
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Title
                title_el = card.find(class_="card-title") or card.find("h3") or card.find("h2") or card.find(class_="title")
                title = title_el.get_text().strip() if title_el else ""
                
                # Sift out title text (Remote.co prepends title with company in some headers)
                if not title:
                    title = link_el.get_text().strip()
                if not title:
                    title = "Remote Opportunity"
                    
                # Clean title if it contains company name or remote badges
                # e.g., "Company Name is hiring a Job Title" -> split or clean
                
                # Company
                company_el = card.find(class_="company-name") or card.find(class_="co") or card.find("span", class_="m-0")
                company = company_el.get_text().strip() if company_el else "Remote.co Employer"
                if " | " in company:
                    company = company.split(" | ")[0]
                
                # Description
                desc_el = card.find(class_="card-text") or card.find(class_="description") or card.find(class_="summary")
                description = desc_el.get_text().strip() if desc_el else f"Remote internship or entry-level opportunity for {title} at {company}."
                
                # Salary extraction if shown
                salary = ""
                salary_el = card.find(class_="salary") or card.find(class_="job-salary") or card.find(text=lambda t: t and ("$" in t or "USD" in t))
                if salary_el:
                    salary_text = salary_el.get_text() if hasattr(salary_el, 'get_text') else str(salary_el)
                    salary = salary_text.strip()
                
                # Image URL (Company Logo)
                img_el = card.find("img")
                image_url = ""
                if img_el and img_el.get("src"):
                    image_url = img_el["src"]
                    if not image_url.startswith("http"):
                        image_url = "https://remote.co" + image_url
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    source="remote_co",
                    source_url=source_url,
                    location="Remote — Work from Anywhere",
                    image_url=image_url,
                    salary=salary,
                    is_remote=True,
                    is_international=True
                )
                
                # Override parish to Jamaica as required (student works from Jamaica)
                job_dict["parish"] = "Jamaica"
                
                jobs.append(job_dict)
                inserted += 1
                found += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("remote_co", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("remote_co", e)
        log_scraper_done("remote_co", found, inserted, skipped)
        
    return jobs
