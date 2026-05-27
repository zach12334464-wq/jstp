import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.config import COMPANY_CAREERS_PAGES
from scraper.utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from scraper.utils.logger import log_scraper_start, log_scraper_done, log_scraper_error
from loguru import logger

def scrape() -> list[dict]:
    """Visits the careers pages of major Jamaican companies and scrapes their job listings."""
    log_scraper_start("company_pages")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    for company_info in COMPANY_CAREERS_PAGES:
        company_name = company_info["name"]
        careers_url = company_info["url"]
        
        try:
            logger.info(f"[COMPANY_PAGES] Scraping careers page for: {company_name}")
            
            # Polite delay between each company careers page request
            polite_delay(extra=1.0)
            
            headers = {
                "User-Agent": get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Referer": "https://www.google.com/"
            }
            
            response = requests.get(careers_url, headers=headers, timeout=15)
            if response.status_code != 200:
                logger.warning(f"[COMPANY_PAGES] Failed to fetch careers page for {company_name}. Status: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for common job listing elements: table rows, lists, division cards, or anchor tags
            # We want to identify links that look like job posts
            links = soup.find_all("a", href=True)
            job_links = []
            
            for link in links:
                href = link["href"].lower()
                text = link.get_text().strip().lower()
                
                # Filter links that are likely to represent individual job openings or career postings
                is_career_link = any(kw in href for kw in ["job", "vacancy", "career", "position", "apply", "opening", "opportunity"]) or \
                                 any(kw in text for kw in ["apply", "view job", "read more", "position", "opening"])
                                 
                # Avoid main navigation and other general links
                is_noise = any(noise in href for noise in ["facebook", "twitter", "linkedin", "instagram", "contact", "about-us", "privacy", "terms"])
                
                if is_career_link and not is_noise:
                    job_links.append(link)
            
            # If no anchor links matched, let's look for standard elements
            cards = soup.select("li") or soup.select("tr") or soup.select("div[class*='job']") or soup.select("div[class*='career']")
            
            if job_links:
                for link in job_links:
                    try:
                        title_text = link.get_text().strip()
                        # Clean title_text or fallback if it's too generic like "Apply"
                        if not title_text or len(title_text) < 4 or title_text.lower() in ["apply", "apply now", "view", "view job", "read more"]:
                            # Look at sibling or parent elements to extract title
                            parent = link.find_parent()
                            title_text = parent.get_text().strip().split("\n")[0] if parent else ""
                            
                        if not title_text or len(title_text) > 100:
                            title_text = f"Career Opportunity at {company_name}"
                            
                        source_url = link["href"]
                        if not source_url.startswith("http"):
                            # Resolve relative URL using host prefix
                            from urllib.parse import urljoin
                            source_url = urljoin(careers_url, source_url)
                            
                        # Deduplicate in run
                        if any(j["source_url"] == source_url for j in jobs):
                            continue
                            
                        # Build job dictionary
                        job_dict = build_job_dict(
                            title=title_text,
                            company=company_name,
                            description=f"Explore exciting career opportunities at {company_name}. Visit their official careers portal for requirements, roles, and benefits.",
                            source="company_pages",
                            source_url=source_url,
                            location="Jamaica",
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
            elif cards:
                # Fallback to lists / card structures
                for card in cards[:15]:  # limit to top 15 elements to avoid spam
                    try:
                        link_el = card.find("a", href=True)
                        if not link_el:
                            continue
                            
                        source_url = link_el["href"]
                        if not source_url.startswith("http"):
                            from urllib.parse import urljoin
                            source_url = urljoin(careers_url, source_url)
                            
                        if any(j["source_url"] == source_url for j in jobs):
                            continue
                            
                        title_text = card.get_text().strip().split("\n")[0]
                        if not title_text or len(title_text) > 100:
                            title_text = link_el.get_text().strip()
                        if not title_text:
                            title_text = f"Career Opportunity at {company_name}"
                            
                        job_dict = build_job_dict(
                            title=title_text,
                            company=company_name,
                            description=f"Explore career opportunities at {company_name}. Complete requirements and job descriptions are available on the careers portal.",
                            source="company_pages",
                            source_url=source_url,
                            location="Jamaica",
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
                        
        except Exception as e:
            logger.error(f"[COMPANY_PAGES] Error scraping {company_name}: {e}")
            continue

    log_scraper_done("company_pages", found, inserted, skipped)
    return jobs
