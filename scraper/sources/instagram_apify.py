import os
from apify_client import ApifyClient
from utils.helpers import build_job_dict
from utils.logger import log_scraper_start, log_scraper_done, log_scraper_error
from loguru import logger

# Configurable constants for Apify
HASHTAGS = ["jamaicajobs", "hiringjamaica", "jamaicainternship", "kingstonjobs", "jamaicacareers"]
RESULTS_PER_HASHTAG = 15

def scrape() -> list[dict]:
    log_scraper_start("instagram_apify")
    
    jobs: list[dict] = []
    found = 0
    inserted = 0
    skipped = 0

    apify_token = os.getenv("APIFY_API_TOKEN")
    if not apify_token:
        logger.error("[INSTAGRAM_APIFY] Missing APIFY_API_TOKEN in environment. Skipping scraper.")
        log_scraper_done("instagram_apify", found, inserted, skipped)
        return jobs

    client = ApifyClient(apify_token)

    try:
        run_input = {
            "search": HASHTAGS,
            "resultsLimit": RESULTS_PER_HASHTAG
        }
        
        logger.info(f"[INSTAGRAM_APIFY] Calling apify/instagram-search-scraper for {len(HASHTAGS)} hashtags (Limit: {RESULTS_PER_HASHTAG} each).")
        
        # Call the Apify actor
        run = client.actor("apify/instagram-search-scraper").call(run_input=run_input)
        dataset_id = run["defaultDatasetId"]
        
        # Iterate over results
        items = client.dataset(dataset_id).iterate_items()
        
        count = 0
        for item in items:
            count += 1
            caption = item.get("caption", item.get("text", ""))
            owner = item.get("ownerUsername", item.get("ownerFullName", "Instagram User"))
            url = item.get("url", item.get("postUrl", ""))
            
            timestamp = item.get("timestamp", item.get("takenAt", ""))
            
            if not url or not caption:
                continue
                
            title = f"Instagram Post by {owner}"
            
            job_dict = build_job_dict(
                title=title,
                company=owner,
                description=caption,
                requirements=caption,
                source="instagram_apify",
                source_url=url,
                location="Jamaica",
                image_url=item.get("displayUrl", item.get("imageUrl", "")),
                is_remote=False,
                is_international=False,
            )
            
            if timestamp and len(timestamp) >= 10:
                job_dict["posted_at"] = timestamp[:10]
                
            jobs.append(job_dict)
            found += 1
            inserted += 1
            
        logger.info(f"[INSTAGRAM_APIFY] Apify consumption: {count} results fetched this run.")
            
    except Exception as e:
        logger.error(f"[INSTAGRAM_APIFY] Apify API call failed: {e}")
        log_scraper_error("instagram_apify", e)
        
    log_scraper_done("instagram_apify", found, inserted, skipped)
    return jobs
