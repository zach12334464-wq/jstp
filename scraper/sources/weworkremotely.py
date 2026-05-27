import requests
from bs4 import BeautifulSoup
from datetime import datetime
from scraper.utils.helpers import get_random_user_agent, polite_delay, build_job_dict
from scraper.utils.logger import log_scraper_start, log_scraper_done, log_scraper_error

def scrape() -> list[dict]:
    """Scrapes remote job listings from We Work Remotely."""
    log_scraper_start("weworkremotely")
    jobs = []
    found = 0
    inserted = 0
    skipped = 0

    try:
        url = "https://weworkremotely.com/remote-jobs#job-listings"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://weworkremotely.com/"
        }
        
        polite_delay(extra=1.0)
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch We Work Remotely, status code: {response.status_code}")
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # WWR organizes jobs in sections containing list items
        # Usually inside sections with id/class containing jobs or inside list tags
        cards = soup.select("section.jobs article ul li") or soup.select("li.feature") or soup.select(".jobs ul li")
        
        if not cards:
            links = soup.find_all("a", href=lambda h: h and "/remote-jobs/" in h)
            cards = [link.find_parent("li") or link for link in links]

        for card in cards:
            try:
                # Find the direct job listing anchor tag
                link_el = card if card.name == 'a' else card.find("a", href=lambda h: h and "/remote-jobs/" in h)
                if not link_el or not link_el.get("href"):
                    continue
                    
                source_url = link_el["href"]
                if not source_url.startswith("http"):
                    source_url = "https://weworkremotely.com" + source_url
                    
                # Deduplicate
                if any(j["source_url"] == source_url for j in jobs):
                    continue

                # Title
                title_el = card.find(class_="title") or card.find("span", class_="title") or card.find("h3")
                title = title_el.get_text().strip() if title_el else ""
                if not title:
                    title = link_el.get_text().strip()
                if not title:
                    title = "Remote Opportunity"
                
                # Company
                company_el = card.find(class_="company") or card.find("span", class_="company")
                company = company_el.get_text().strip() if company_el else "We Work Remotely Employer"
                
                # Location (sometimes WWR specifies region restrictions)
                region_el = card.find(class_="region") or card.find("span", class_="region")
                region = region_el.get_text().strip() if region_el else ""
                
                # Description
                description = f"Remote opportunity for {title} at {company}."
                if region:
                    description += f" Region restriction: {region}."
                description += " Please visit We Work Remotely for full requirements."
                
                # Image URL (Company Logo)
                # In WWR, the logo is often set as a background-image style on a div or an img tag
                img_el = card.find("img") or card.find(class_="flag-logo")
                image_url = ""
                if img_el:
                    if img_el.name == 'img' and img_el.get("src"):
                        image_url = img_el["src"]
                    elif img_el.get("style") and "background-image" in img_el.get("style"):
                        # Extract URL from background-image: url(...)
                        style = img_el.get("style")
                        import re
                        match = re.search(r'url\((.*?)\)', style)
                        if match:
                            image_url = match.group(1).replace("'", "").replace('"', "")
                            
                if image_url and not image_url.startswith("http"):
                    image_url = "https://weworkremotely.com" + image_url
                
                # Build job object using build_job_dict helper
                job_dict = build_job_dict(
                    title=title,
                    company=company,
                    description=description,
                    source="weworkremotely",
                    source_url=source_url,
                    location="Remote — Work from Anywhere",
                    image_url=image_url,
                    is_remote=True,
                    is_international=True
                )
                
                # Override parish to Jamaica as required
                job_dict["parish"] = "Jamaica"
                
                jobs.append(job_dict)
                inserted += 1
                found += 1
                
            except Exception as e:
                skipped += 1
                continue
                
        log_scraper_done("weworkremotely", found, inserted, skipped)
        
    except Exception as e:
        log_scraper_error("weworkremotely", e)
        log_scraper_done("weworkremotely", found, inserted, skipped)
        
    return jobs
