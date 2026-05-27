from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from utils.logger import log_scraper_error, log_job_inserted
from utils.freshness import update_freshness_scores, should_archive

from datetime import datetime

supabase: Client = None

def get_client() -> Client:
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase

def insert_job(job: dict) -> bool:
    try:
        db = get_client()
        db.table("jobs").insert(job).execute()
        log_job_inserted(job["title"], job["company"], job["source"])
        return True
    except Exception as e:
        log_scraper_error("database.insert_job", e)
        return False

def insert_jobs_batch(jobs: list) -> tuple[int, int]:
    inserted = 0
    failed = 0
    for job in jobs:
        success = insert_job(job)
        if success:
            inserted += 1
        else:
            failed += 1
    return inserted, failed

def job_exists(title: str, company: str) -> bool:
    try:
        db = get_client()
        result = db.table("jobs")\
            .select("id")\
            .ilike("title", f"%{title}%")\
            .ilike("company", f"%{company}%")\
            .execute()
        return len(result.data) > 0
    except Exception as e:
        log_scraper_error("database.job_exists", e)
        return False

def get_all_active_jobs() -> list:
    try:
        db = get_client()
        result = db.table("jobs")\
            .select("id, title, company, posted_at, freshness_score")\
            .eq("active", True)\
            .execute()
        return result.data or []
    except Exception as e:
        log_scraper_error("database.get_all_active_jobs", e)
        return []

def get_jobs_by_source(source: str) -> list:
    try:
        db = get_client()
        result = db.table("jobs")\
            .select("id, title, company, posted_at")\
            .eq("source", source)\
            .eq("active", True)\
            .execute()
        return result.data or []
    except Exception as e:
        log_scraper_error("database.get_jobs_by_source", e)
        return []

def archive_expired_jobs() -> int:
    try:
        db = get_client()
        active_jobs = get_all_active_jobs()
        archived_count = 0
        for job in active_jobs:
            if should_archive(job.get("posted_at", "")):
                db.table("jobs")\
                    .update({"active": False})\
                    .eq("id", job["id"])\
                    .execute()
                archived_count += 1
        return archived_count
    except Exception as e:
        log_scraper_error("database.archive_expired_jobs", e)
        return 0

def update_freshness_in_db() -> int:
    try:
        db = get_client()
        active_jobs = get_all_active_jobs()
        updated = update_freshness_scores(active_jobs)
        update_count = 0
        for job in updated:
            db.table("jobs")\
                .update({"freshness_score": job["freshness_score"]})\
                .eq("id", job["id"])\
                .execute()
            update_count += 1
        return update_count
    except Exception as e:
        log_scraper_error("database.update_freshness_in_db", e)
        return 0

def get_scraper_stats() -> dict:
    try:
        db = get_client()
        total = db.table("jobs").select("id", count="exact").execute()
        active = db.table("jobs").select("id", count="exact").eq("active", True).execute()
        remote = db.table("jobs").select("id", count="exact").eq("is_remote", True).execute()
        international = db.table("jobs").select("id", count="exact").eq("is_international", True).execute()
        return {
            "total_jobs": total.count or 0,
            "active_jobs": active.count or 0,
            "remote_jobs": remote.count or 0,
            "international_jobs": international.count or 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        log_scraper_error("database.get_scraper_stats", e)
        return {}

def save_scraper_run(source: str, found: int, inserted: int, skipped: int, errors: int):
    try:
        db = get_client()
        db.table("scraper_runs").insert({
            "source": source,
            "found": found,
            "inserted": inserted,
            "skipped": skipped,
            "errors": errors,
            "ran_at": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        log_scraper_error("database.save_scraper_run", e)

