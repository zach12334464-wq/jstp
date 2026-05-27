import argparse
import asyncio
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

# Import scrapers
import sources.gleaner
import sources.caribbeanjobs
import sources.goj
import sources.indeed_jamaica
import sources.company_pages
import sources.remote_co
import sources.weworkremotely
import sources.remotive
import sources.appen
import sources.facebook_ads
import sources.contra
import sources.wellfound

# Import pipeline steps
from ai_classifier import classify_jobs
from deduplicator import filter_duplicates
import database

# Import scheduler config hours
from config import SCHEDULE_LOCAL_HOURS, SCHEDULE_REMOTE_HOURS, SCHEDULE_ADS_HOURS

def execute_scraper_source(name: str, scrape_func) -> list[dict]:
    """Helper to run a scraper source supporting both synchronous and asynchronous functions."""
    logger.info(f"[ORCHESTRATOR] Launching scraper: '{name}'")
    try:
        if asyncio.iscoroutinefunction(scrape_func):
            # Run async function using clean event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            return loop.run_until_complete(scrape_func())
        else:
            return scrape_func()
    except Exception as e:
        logger.error(f"[ORCHESTRATOR] Error occurred running scraper '{name}': {e}")
        return []

def process_and_save_batch(batch_name: str, raw_jobs: list[dict]):
    """Aggregates, deduplicates, classifies, and inserts a batch of scraped jobs into the database."""
    total_found = len(raw_jobs)
    logger.info(f"[ORCHESTRATOR] Processing {total_found} scraped jobs for batch: '{batch_name}'")
    
    if not raw_jobs:
        # Record run metadata even if no items found
        database.save_scraper_run(
            source=batch_name,
            found=0,
            inserted=0,
            skipped=0,
            errors=0
        )
        logger.info(f"[ORCHESTRATOR] Batch '{batch_name}' finished with 0 jobs found.")
        return

    # 1. Deduplicate against active jobs in the DB and current batch
    unique_jobs, duplicate_count = filter_duplicates(raw_jobs)
    logger.info(f"[ORCHESTRATOR] Deduplication done. Found {duplicate_count} duplicates, {len(unique_jobs)} unique jobs remaining.")

    # 2. AI Classifier / Filter
    classified_jobs = classify_jobs(unique_jobs)
    logger.info(f"[ORCHESTRATOR] AI Classification done. {len(classified_jobs)} jobs passed suitability thresholds.")
    
    skipped_count = duplicate_count + (len(unique_jobs) - len(classified_jobs))

    # 3. Database batch insertion
    inserted, failed = database.insert_jobs_batch(classified_jobs)
    logger.info(f"[ORCHESTRATOR] DB insertion done. Inserted: {inserted} | Failed: {failed}")

    # 4. Run maintenance (Archiving expired & updating freshness labels)
    archived = database.archive_expired_jobs()
    if archived > 0:
        logger.info(f"[ORCHESTRATOR] Archived {archived} stale jobs from database.")

    updated = database.update_freshness_in_db()
    if updated > 0:
        logger.info(f"[ORCHESTRATOR] Updated freshness score labels for {updated} active jobs.")

    # 5. Save run statistics
    database.save_scraper_run(
        source=batch_name,
        found=total_found,
        inserted=inserted,
        skipped=skipped_count,
        errors=failed
    )
    
    logger.info(
        f"[ORCHESTRATOR] FINAL SUMMARY [{batch_name.upper()}] — Found: {total_found} | "
        f"Inserted: {inserted} | Skipped: {skipped_count} | Failed: {failed}"
    )

def run_local_sources():
    """Runs all local job board and company page scrapers."""
    logger.info("[ORCHESTRATOR] Starting local source scrapers...")
    raw_jobs = []
    
    raw_jobs.extend(execute_scraper_source("gleaner", sources.gleaner.scrape))
    raw_jobs.extend(execute_scraper_source("caribbeanjobs", sources.caribbeanjobs.scrape))
    raw_jobs.extend(execute_scraper_source("goj", sources.goj.scrape))
    raw_jobs.extend(execute_scraper_source("indeed_jamaica", sources.indeed_jamaica.scrape))
    raw_jobs.extend(execute_scraper_source("company_pages", sources.company_pages.scrape))
    
    process_and_save_batch("local_sources", raw_jobs)

def run_remote_sources():
    """Runs all remote, API, freelance, and startup internship scrapers."""
    logger.info("[ORCHESTRATOR] Starting remote source scrapers...")
    raw_jobs = []
    
    raw_jobs.extend(execute_scraper_source("remote_co", sources.remote_co.scrape))
    raw_jobs.extend(execute_scraper_source("weworkremotely", sources.weworkremotely.scrape))
    raw_jobs.extend(execute_scraper_source("remotive", sources.remotive.scrape))
    raw_jobs.extend(execute_scraper_source("appen", sources.appen.scrape))
    raw_jobs.extend(execute_scraper_source("contra", sources.contra.scrape))
    raw_jobs.extend(execute_scraper_source("wellfound", sources.wellfound.scrape))
    
    process_and_save_batch("remote_sources", raw_jobs)

def run_ads_sources():
    """Runs all social media/ad library scrapers."""
    logger.info("[ORCHESTRATOR] Starting ad-library source scrapers...")
    raw_jobs = []
    
    raw_jobs.extend(execute_scraper_source("facebook_ads", sources.facebook_ads.scrape))
    
    process_and_save_batch("facebook_ads", raw_jobs)

def run_all():
    """Runs all scraper categories sequentially."""
    logger.info("[ORCHESTRATOR] Executing a complete sweep of all scraper sources...")
    run_local_sources()
    run_remote_sources()
    run_ads_sources()
    logger.info("[ORCHESTRATOR] Full sweep execution completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JSTP Scraper Orchestration Pipeline")
    parser.add_argument(
        "--run-now",
        action="store_true",
        help="Run all scrapers immediately once and exit without launching the scheduler"
    )
    args = parser.parse_args()

    if args.run_now:
        logger.info("[ORCHESTRATOR] CLI flag '--run-now' received. Starting immediate execution.")
        try:
            run_all()
        except KeyboardInterrupt:
            logger.warning("[ORCHESTRATOR] Execution interrupted by user.")
            sys.exit(1)
        logger.info("[ORCHESTRATOR] Execution completed. Exiting.")
        sys.exit(0)

    # Scheduler Setup using BlockingScheduler
    scheduler = BlockingScheduler()

    # Schedule category tasks at their configured hours
    for hour in SCHEDULE_LOCAL_HOURS:
        scheduler.add_job(run_local_sources, 'cron', hour=hour, minute=0, id=f"local_cron_{hour}")
    
    for hour in SCHEDULE_REMOTE_HOURS:
        scheduler.add_job(run_remote_sources, 'cron', hour=hour, minute=0, id=f"remote_cron_{hour}")
        
    for hour in SCHEDULE_ADS_HOURS:
        scheduler.add_job(run_ads_sources, 'cron', hour=hour, minute=0, id=f"ads_cron_{hour}")

    logger.info("[ORCHESTRATOR] Scheduler successfully configured.")
    logger.info(f"[ORCHESTRATOR] Scheduled Local hours: {SCHEDULE_LOCAL_HOURS}")
    logger.info(f"[ORCHESTRATOR] Scheduled Remote hours: {SCHEDULE_REMOTE_HOURS}")
    logger.info(f"[ORCHESTRATOR] Scheduled Ads hours: {SCHEDULE_ADS_HOURS}")

    try:
        # Run all once immediately upon startup
        logger.info("[ORCHESTRATOR] Performing initial startup crawl...")
        run_all()
        
        logger.info("[ORCHESTRATOR] Initial crawl done. Starting APScheduler loop...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.warning("[ORCHESTRATOR] Scheduler shutting down due to KeyboardInterrupt.")
        scheduler.shutdown(wait=False)
        sys.exit(0)
    except Exception as start_err:
        logger.error(f"[ORCHESTRATOR] Critical pipeline startup error: {start_err}")
        sys.exit(1)
