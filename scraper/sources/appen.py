import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error


def scrape() -> list[dict]:
    """Scrapes remote micro-task and data annotation jobs from Appen."""
    log_scraper_start("appen")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://appen.com/jobs/"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://appen.com/"
        }
        
        polite_delay(extra=1.0)
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch Appen jobs, status code: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Target job links or card containers (e.g. Greenhouse listing, custom board blocks)
        cards = soup.select(".job-list li") or soup.select(".job-listing") or soup.select("article")
        
        # Fallback to general link checking
        if not cards:
            links = soup.find_all("a", href=lambda h: h and ("greenhouse.io" in h or "/jobs/" in h or "careers" in h))
            cards = [link.find_parent("div") or link for link in links]

        for card in cards:
            try:
                # Find link to job details
                link_el = card if card.name == 'a' else card.find("a", href=True)
                if not link_el or not link_el.get("href"):
                    continue
                    
                source_url = link_el["href"]
                # Filter out obvious noisy links
                if not any(source_url.startswith(prefix) for prefix in ["http", "/"]):
                    continue
                    
                if source_url.startswith("/"):
                    source_url = "https://appen.com" + source_url
                    
                # Skip social and navigation items
                if any(noise in source_url for noise in ["facebook", "twitter", "linkedin", "instagram", "contact", "about"]):
                    continue
                    
                # Deduplicate
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Title
                title_el = card.find("h3") or card.find("h2") or card.find(class_="title") or link_el
                title = title_el.get_text().strip() if title_el else ""
                if not title or title == source_url:
                    title = link_el.get_text().strip()
                if not title:
                    title = "Data Annotation Contributor"
                
                # Description
                desc_el = card.find(class_="description") or card.find(class_="summary")
                description = desc_el.get_text().strip() if desc_el else f"Join Appen as a {title}. Work on high-impact AI training and data annotation tasks from the comfort of your home."
                
                # Salary/hourly rate extraction
                salary = ""
                salary_el = card.find(text=lambda t: t and ("$/hr" in t.lower() or "per hour" in t.lower() or "usd" in t.lower()))
                if salary_el:
                    salary = salary_el.strip()
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company="Appen",
                    description=description,
                    source="appen",
                    source_url=source_url,
                    location="Remote — Work from Anywhere",
                    image_url="",
                    salary=salary,
                    is_remote=True,
                    is_international=True,
                    payment_methods=["PayPal", "Payoneer"]
                )
                
                # Override parish to Jamaica as required
                job_dict["parish"] = "Jamaica"
                
                jobs.append(job_dict)
                inserted += 1
                found += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("appen", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("appen", e)
        log_scraper_done("appen", found, inserted, skipped)
        
    return jobs
