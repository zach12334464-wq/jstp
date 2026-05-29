import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error


def scrape() -> list[dict]:
    """Scrapes job listings from Jamaica Gleaner."""
    log_scraper_start("gleaner")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://www.jamaica-gleaner.com/section/careers"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

        # Polite delay before requests
        polite_delay(extra=1.0)

        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            log_scraper_error("gleaner", Exception(f"Failed to fetch Gleaner jobs page, status code: {response.status_code}"))
            log_scraper_done("gleaner", found, inserted, skipped)
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Target common listing structures
        cards = soup.select("div.views-row") or soup.select(".job-listing") or soup.select("article")
        
        # Fallback if no cards found
        if not cards:
            links = soup.find_all("a", href=lambda h: h and "/jobs/" in h)
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
                    source_url = "https://jamaica-gleaner.com" + source_url
                    
                # Deduplicate within this single run batch
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Title
                title_el = card.find("h3") or card.find("h2") or card.find(class_="title") or link_el
                title = title_el.get_text().strip() if title_el else "Job Vacancy"
                if title == source_url or not title:
                    title = link_el.get_text().strip()
                if not title:
                    title = "Job Opportunity"
                
                # Company
                company_el = card.find(class_="company") or card.find(class_="views-field-field-job-employer")
                company = company_el.get_text().strip() if company_el else "Jamaica Gleaner"
                
                # Location
                location_el = card.find(class_="location") or card.find(class_="views-field-field-job-location")
                location = location_el.get_text().strip() if location_el else "Jamaica"
                
                # Description
                desc_el = card.find(class_="description") or card.find(class_="body") or card.find(class_="views-field-body")
                description = desc_el.get_text().strip() if desc_el else f"Job opportunity at {company}. Please visit Gleaner jobs for more details."
                
                # Image
                img_el = card.find("img")
                image_url = ""
                if img_el and img_el.get("src"):
                    image_url = img_el["src"]
                    if not image_url.startswith("http"):
                        image_url = "https://jamaica-gleaner.com" + image_url
                
                requirements_text = description

                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    requirements=requirements_text,
                    source="gleaner",
                    source_url=source_url,
                    location=location,
                    image_url=image_url,
                    is_remote=False,
                    is_international=False
                )
                
                jobs.append(job_dict)
                inserted += 1
                found += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("gleaner", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("gleaner", e)
        log_scraper_done("gleaner", found, inserted, skipped)
        
    return jobs
