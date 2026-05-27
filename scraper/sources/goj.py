import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from scraper.utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

def scrape() -> list[dict]:
    """Scrapes job listings from the Government of Jamaica Public Service Commission."""
    log_scraper_start("goj")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://psc.gov.jm/vacancies"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://psc.gov.jm/"
        }
        
        polite_delay(extra=1.0)
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch GOJ vacancies, status code: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Government websites frequently structure listings using tables or views rows
        cards = soup.select("table tbody tr") or soup.select(".views-row") or soup.select(".vacancy-item")
        
        # Fallback to broad anchor tag matching
        if not cards:
            links = soup.find_all("a", href=lambda h: h and ("/vacancies/" in h or "/vacancy/" in h))
            cards = [link.find_parent("div") or link for link in links]

        for card in cards:
            try:
                # Find link to the vacancy
                link_el = card.find("a", href=True)
                if not link_el:
                    link_el = card if (card.name == 'a' and card.get("href")) else None
                if not link_el:
                    continue
                    
                source_url = link_el["href"]
                if not source_url.startswith("http"):
                    source_url = "https://psc.gov.jm" + source_url
                    
                # Deduplicate
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Title and Company details
                # In tables, they may be in separate <td> elements
                tds = card.find_all("td")
                
                title = ""
                company = ""
                description = ""
                
                if len(tds) >= 2:
                    title = tds[0].get_text().strip()
                    company = tds[1].get_text().strip()
                    if len(tds) >= 3:
                        description = tds[2].get_text().strip()
                else:
                    title_el = card.find(class_="title") or card.find(class_="vacancy-title") or link_el
                    title = title_el.get_text().strip() if title_el else "Public Service Vacancy"
                    
                    company_el = card.find(class_="ministry") or card.find(class_="department") or card.find(class_="views-field-field-ministry")
                    company = company_el.get_text().strip() if company_el else "Government of Jamaica"
                
                if not title or title == source_url:
                    title = link_el.get_text().strip() or "Public Service Vacancy"
                if not company:
                    company = "Government of Jamaica"
                if not description:
                    description = f"Government vacancy for {title} at {company}. Please visit the Public Service Commission website to view full specifications."
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    source="goj",
                    source_url=source_url,
                    location="Jamaica",
                    image_url="",
                    is_remote=False,
                    is_international=False
                )
                
                # Override industry default to Government as required
                job_dict["industry"] = "Government"
                
                jobs.append(job_dict)
                inserted += 1
                found += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("goj", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("goj", e)
        log_scraper_done("goj", found, inserted, skipped)
        
    return jobs
