from loguru import logger
import sys
import os

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Remove default handler
logger.remove()

# Console handler — clean and readable
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> — {message}",
    level="INFO",
    colorize=True,
)

# File handler — full debug log
logger.add(
    os.path.join(LOG_DIR, "scraper_{time:YYYY-MM-DD}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} — {message}",
    level="DEBUG",
    rotation="1 day",
    retention="7 days",
    compression="zip",
)

# Separate error log
logger.add(
    os.path.join(LOG_DIR, "errors_{time:YYYY-MM-DD}.log"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} — {message}",
    level="ERROR",
    rotation="1 week",
    retention="30 days",
)


def log_scraper_start(source: str):
    logger.info(f"[{source.upper()}] Scraper started")


def log_scraper_done(source: str, found: int, inserted: int, skipped: int):
    logger.info(
        f"[{source.upper()}] Done — found: {found} | inserted: {inserted} | skipped: {skipped}"
    )


def log_scraper_error(source: str, error: Exception):
    logger.error(f"[{source.upper()}] Error — {type(error).__name__}: {error}")


def log_job_discarded(title: str, reason: str):
    logger.debug(f"DISCARDED — {title[:50]} | reason: {reason}")


def log_job_inserted(title: str, company: str, source: str):
    logger.debug(f"INSERTED — {title[:50]} | {company} | source: {source}")


def log_duplicate(title: str, company: str):
    logger.debug(f"DUPLICATE — {title[:50]} | {company}")


def log_ai_batch(batch_size: int, passed: int, failed: int):
    logger.info(f"AI BATCH — size: {batch_size} | passed: {passed} | failed: {failed}")

