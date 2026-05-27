import random
import time
import re
from datetime import datetime
from scraper.config import USER_AGENTS, REQUEST_DELAY, STUDENT_KEYWORDS, DISCARD_KEYWORDS, SCAM_KEYWORDS, REMOTE_BLOCKLIST

def get_random_user_agent() -> str:
    return random.choice(USER_AGENTS)

def polite_delay(extra: float = 0):
    time.sleep(REQUEST_DELAY + extra + random.uniform(0.5, 1.5))

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def extract_parish(text: str) -> str:
    parishes = [
        "Kingston", "St Andrew", "St Catherine", "Clarendon",
        "Manchester", "St Elizabeth", "Westmoreland", "Hanover",
        "St James", "Trelawny", "St Ann", "St Mary",
        "Portland", "St Thomas"
    ]
    text_lower = text.lower()
    for parish in parishes:
        if parish.lower() in text_lower:
            return parish
    if "kingston" in text_lower or "new kingston" in text_lower:
        return "Kingston"
    if "montego" in text_lower or "mobay" in text_lower:
        return "St James"
    if "spanish town" in text_lower:
        return "St Catherine"
    if "mandeville" in text_lower:
        return "Manchester"
    if "portmore" in text_lower:
        return "St Catherine"
    if "ocho rios" in text_lower:
        return "St Ann"
    if "may pen" in text_lower:
        return "Clarendon"
    return "Jamaica"

def extract_job_type(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["intern", "internship", "placement"]):
        return "Internship"
    if any(w in text_lower for w in ["part-time", "part time", "parttime"]):
        return "Part-time"
    if any(w in text_lower for w in ["summer", "seasonal", "temporary", "temp"]):
        return "Summer Job"
    if any(w in text_lower for w in ["remote", "work from home", "wfh", "anywhere"]):
        return "Remote"
    return "Full-time"

def extract_industry(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["tech", "software", "developer", "it ", "digital", "data", "cyber"]):
        return "Technology"
    if any(w in text_lower for w in ["finance", "banking", "accounting", "audit", "financial"]):
        return "Finance"
    if any(w in text_lower for w in ["market", "brand", "advertis", "pr ", "social media", "content"]):
        return "Marketing"
    if any(w in text_lower for w in ["health", "medical", "nurse", "hospital", "clinical", "pharma"]):
        return "Healthcare"
    if any(w in text_lower for w in ["teach", "educat", "school", "tutor", "academic"]):
        return "Education"
    if any(w in text_lower for w in ["media", "journal", "broadcast", "film", "radio", "tv ", "news"]):
        return "Media"
    if any(w in text_lower for w in ["government", "ministry", "public sector", "civil service"]):
        return "Government"
    if any(w in text_lower for w in ["retail", "shop", "store", "sales", "customer service"]):
        return "Retail"
    if any(w in text_lower for w in ["legal", "law", "attorney", "paralegal"]):
        return "Legal"
    if any(w in text_lower for w in ["engineering", "mechanical", "electrical", "civil eng"]):
        return "Engineering"
    return "Business"

def rule_based_filter(title: str, description: str) -> tuple[bool, str]:
    combined = (title + " " + description).lower()
    for keyword in SCAM_KEYWORDS:
        if keyword in combined:
            return False, f"scam keyword: {keyword}"
    for keyword in DISCARD_KEYWORDS:
        if keyword in combined:
            return False, f"discard keyword: {keyword}"
    return True, "passed"

def is_student_relevant(title: str, description: str) -> bool:
    combined = (title + " " + description).lower()
    return any(keyword in combined for keyword in STUDENT_KEYWORDS)

def is_remote_blocked(description: str) -> bool:
    desc_lower = description.lower()
    return any(phrase in desc_lower for phrase in REMOTE_BLOCKLIST)

def parse_date(date_str: str) -> str:
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    formats = [
        "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
        "%B %d, %Y", "%d %B %Y", "%b %d, %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return datetime.now().strftime("%Y-%m-%d")

def build_job_dict(
    title: str,
    company: str,
    description: str,
    source: str,
    source_url: str,
    location: str = "",
    image_url: str = "",
    salary: str = "",
    deadline: str = "",
    is_remote: bool = False,
    is_international: bool = False,
    payment_methods: list = []
) -> dict:
    return {
        "title": clean_text(title),
        "company": clean_text(company),
        "description": clean_text(description),
        "location": clean_text(location),
        "parish": extract_parish(location + " " + description),
        "type": extract_job_type(title + " " + description),
        "industry": extract_industry(title + " " + description),
        "academic_level": "Any",
        "salary": clean_text(salary),
        "deadline": parse_date(deadline),
        "source": source,
        "source_url": source_url,
        "image_url": clean_text(image_url),
        "is_remote": is_remote,
        "is_international": is_international,
        "payment_methods": payment_methods,
        "posted_at": datetime.now().strftime("%Y-%m-%d"),
        "freshness_score": 100,
        "ai_relevance_score": None,
        "ai_scam_score": None,
        "verified": False,
        "active": True
    }

