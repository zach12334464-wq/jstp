from datetime import datetime, timedelta
from config import FRESHNESS_DAYS


def calculate_freshness_score(posted_at: str) -> int:
    try:
        posted_date = datetime.strptime(posted_at, "%Y-%m-%d")
    except ValueError:
        return 50

    today = datetime.now()
    days_old = (today - posted_date).days

    if days_old <= 1:
        return 100
    elif days_old <= 3:
        return 95
    elif days_old <= 7:
        return 85
    elif days_old <= 14:
        return 70
    elif days_old <= 21:
        return 50
    elif days_old <= FRESHNESS_DAYS:
        return 25
    else:
        return 0


def is_expired(posted_at: str) -> bool:
    return calculate_freshness_score(posted_at) == 0


def get_expiry_date(posted_at: str) -> str:
    try:
        posted_date = datetime.strptime(posted_at, "%Y-%m-%d")
    except ValueError:
        posted_date = datetime.now()
    expiry = posted_date + timedelta(days=FRESHNESS_DAYS)
    return expiry.strftime("%Y-%m-%d")


def get_freshness_label(score: int) -> str:
    if score >= 95:
        return "Just Posted"
    elif score >= 85:
        return "This Week"
    elif score >= 70:
        return "2 Weeks Ago"
    elif score >= 50:
        return "3 Weeks Ago"
    elif score >= 25:
        return "This Month"
    else:
        return "Expired"


def should_archive(posted_at: str) -> bool:
    return is_expired(posted_at)


def update_freshness_scores(jobs: list) -> list:
    for job in jobs:
        posted = job.get("posted_at", "")
        job["freshness_score"] = calculate_freshness_score(posted)
        job["freshness_label"] = get_freshness_label(job["freshness_score"])
    return jobs

