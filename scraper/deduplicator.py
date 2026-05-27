from fuzzywuzzy import fuzz
from database import get_all_active_jobs, get_jobs_by_source
from utils.logger import log_duplicate

# Minimum similarity score to consider two jobs duplicates (0-100)
DUPLICATE_THRESHOLD = 85

_cached_jobs = []
_cache_loaded = False

def load_cache():
    global _cached_jobs, _cache_loaded
    _cached_jobs = get_all_active_jobs()
    _cache_loaded = True


def refresh_cache():
    global _cached_jobs, _cache_loaded
    _cached_jobs = get_all_active_jobs()
    _cache_loaded = True


def is_duplicate(title: str, company: str) -> bool:
    global _cached_jobs, _cache_loaded

    if not _cache_loaded:
        load_cache()

    title_clean = title.lower().strip()
    company_clean = company.lower().strip()

    for existing in _cached_jobs:
        existing_title = existing.get("title", "").lower().strip()
        existing_company = existing.get("company", "").lower().strip()

        # Exact match first — fastest check
        if title_clean == existing_title and company_clean == existing_company:
            log_duplicate(title, company)
            return True

        # Fuzzy match on title if same company
        if company_clean == existing_company:
            title_similarity = fuzz.ratio(title_clean, existing_title)
            if title_similarity >= DUPLICATE_THRESHOLD:
                log_duplicate(title, company)
                return True

        # Fuzzy match on both title and company
        title_similarity = fuzz.ratio(title_clean, existing_title)
        company_similarity = fuzz.ratio(company_clean, existing_company)

        if (
            title_similarity >= DUPLICATE_THRESHOLD
            and company_similarity >= DUPLICATE_THRESHOLD
        ):
            log_duplicate(title, company)
            return True

    return False


def filter_duplicates(jobs: list) -> tuple[list, int]:
    unique_jobs = []
    duplicate_count = 0
    seen_in_batch = set()

    for job in jobs:
        title = job.get("title", "")
        company = job.get("company", "")
        batch_key = f"{title.lower()}_{company.lower()}"

        # Check within current batch first
        if batch_key in seen_in_batch:
            duplicate_count += 1
            continue

        # Check against database
        if is_duplicate(title, company):
            duplicate_count += 1
            continue

        unique_jobs.append(job)
        seen_in_batch.add(batch_key)

        # Add to cache so next job in batch can check against it
        _cached_jobs.append(
            {
                "title": title,
                "company": company,
                "posted_at": job.get("posted_at", ""),
                "freshness_score": job.get("freshness_score", 100),
            }
        )

    return unique_jobs, duplicate_count


def get_duplicate_stats() -> dict:
    total = len(_cached_jobs)
    return {
        "cached_jobs": total,
        "cache_loaded": _cache_loaded,
    }

