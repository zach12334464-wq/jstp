import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ModuleNotFoundError:
    # Allow running without dotenv installed (e.g., in minimal environments)
    pass


# ── Supabase ────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ── Groq ────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Scraper settings ────────────────────────────
REQUEST_DELAY = 2  # seconds between requests
REQUEST_TIMEOUT = 15  # seconds before timeout
MAX_RETRIES = 3  # retries on failure
BATCH_SIZE = 10  # jobs per Groq batch call
FRESHNESS_DAYS = 30  # days before a job is considered stale
MIN_RELEVANCE_SCORE = 0.55  # minimum AI relevance to keep a job
MAX_SCAM_SCORE = 0.40  # maximum AI scam score before discard

# ── Scheduler ───────────────────────────────────
SCHEDULE_LOCAL_HOURS = [0, 12]  # run local scrapers at midnight and noon
SCHEDULE_REMOTE_HOURS = [6, 18]  # run remote scrapers at 6am and 6pm
SCHEDULE_ADS_HOURS = [9, 21]  # run ad library scrapers at 9am and 9pm
SCHEDULE_CAREERS_HOURS = [3, 15]  # run company careers pages at 3am and 3pm

# ── Rule-based filters (free, no Groq) ──────────
STUDENT_KEYWORDS = [
    "intern",
    "internship",
    "part-time",
    "part time",
    "summer",
    "trainee",
    "entry level",
    "entry-level",
    "graduate",
    "student",
    "junior",
    "assistant",
    "temporary",
    "temp",
    "seasonal",
    "placement",
]

DISCARD_KEYWORDS = [
    "senior",
    "manager",
    "director",
    "vp ",
    "vice president",
    "head of",
    "chief",
    "cto",
    "ceo",
    "cfo",
    "principal",
    "10 years",
    "8 years",
    "7 years",
    "5+ years",
    "5 years experience",
    "minimum 5",
]

SCAM_KEYWORDS = [
    "upfront payment",
    "pay to work",
    "registration fee",
    "training fee",
    "buy our kit",
    "invest now",
    "guaranteed income",
    "work from home unlimited",
    "no experience unlimited pay",
    "mlm",
    "network marketing",
    "pyramid",
    "send money first",
]

# ── Remote filter ────────────────────────────────
REMOTE_BLOCKLIST = [
    "us only",
    "usa only",
    "united states only",
    "must be located in",
    "must reside in",
    "eu only",
    "uk only",
    "canada only",
    "requires ssn",
    "social security number",
    "requires work authorization",
]

REMOTE_PAYMENT_KEYWORDS = [
    "payoneer",
    "paypal",
    "wise",
    "transferwise",
    "usd",
    "us dollars",
    "international transfer",
    "cryptocurrency",
    "crypto",
]

# ── Jamaican company careers pages ───────────────
COMPANY_CAREERS_PAGES = [
    {"name": "Digicel Jamaica", "url": "https://www.digicelgroup.com/jm/en/careers.html"},
    {"name": "GraceKennedy", "url": "https://www.gracekennedy.com/careers"},
    {"name": "NCB Financial Group", "url": "https://www.ncbfg.com/careers"},
    {
        "name": "Scotiabank Jamaica",
        "url": "https://www.scotiabank.com/jm/en/personal/about-scotiabank/careers.html",
    },
    {"name": "Sagicor Group Jamaica", "url": "https://www.sagicorjamaica.com/about-us/careers"},
    {"name": "JMMB Group", "url": "https://www.jmmb.com/careers"},
    {"name": "Flow Jamaica", "url": "https://discoverflow.co/jm/careers"},
    {"name": "Courts Jamaica", "url": "https://www.courtsjamaica.com/careers"},
    {"name": "Jamaica Broilers", "url": "https://jamaicabroilers.com/careers"},
    {"name": "Carib Cement", "url": "https://caribcement.com/careers"},
    {"name": "Jamaica National", "url": "https://jngroup.com/careers"},
    {"name": "Seprod Group", "url": "https://seprod.com/careers"},
]

# ── Facebook Ad Library ──────────────────────────
FACEBOOK_AD_LIBRARY_URL = "https://www.facebook.com/ads/library"
FACEBOOK_AD_SEARCH_TERMS = [
    "hiring",
    "vacancy",
    "now recruiting",
    "internship",
    "job opening",
    "we are hiring",
    "join our team",
    "apply now",
    "part time",
    "summer job",
]
FACEBOOK_AD_COUNTRY = "JM"

# ── Instagram hashtags ───────────────────────────
INSTAGRAM_HASHTAGS = [
    "jamaicajobs",
    "kingstonjobs",
    "jamaicahiring",
    "jobsinjamaica",
    "jamaicainternship",
    "caribbeanjobs",
    "jamaicawork",
    "montegobaywork",
    "jobsja",
]

# ── Remote job sources ───────────────────────────
REMOTE_SOURCES = {
    "remote_co": "https://remote.co/remote-jobs/",
    "weworkremotely": "https://weworkremotely.com/remote-jobs",
    "remotive": "https://remotive.com/remote-jobs",
    "appen": "https://appen.com/jobs/",
    "contra": "https://contra.com/jobs",
    "wellfound": "https://wellfound.com/jobs",
}

# ── User agents (rotate to avoid blocks) ─────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
]

