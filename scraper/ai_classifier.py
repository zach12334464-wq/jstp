import json
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, BATCH_SIZE, MIN_RELEVANCE_SCORE, MAX_SCAM_SCORE
from utils.helpers import rule_based_filter, is_student_relevant
from utils.logger import log_ai_batch, log_job_discarded

from loguru import logger

def _rule_based_fallback(title: str, description: str) -> tuple[float, float]:
    """Helper to compute fallback relevance and scam scores based on keywords."""
    passed, reason = rule_based_filter(title, description)
    if not passed:
        if "scam" in reason:
            return 0.10, 0.90  # Unsuitable, highly likely a scam
        else:
            return 0.10, 0.05  # Unsuitable (e.g. senior/manager keyword), not a scam
    else:
        # Check student keyword presence
        is_student = is_student_relevant(title, description)
        relevance = 0.80 if is_student else 0.40
        return relevance, 0.05

def classify_jobs(jobs: list[dict]) -> list[dict]:
    """Classifies the relevance and safety of job listings using Groq AI with a robust fallback."""
    if not jobs:
        return []

    logger.info(f"[AI_CLASSIFIER] Starting AI classification for {len(jobs)} jobs...")
    
    # If API key is missing, go straight to fallback to save startup time
    if not GROQ_API_KEY:
        logger.warning("[AI_CLASSIFIER] GROQ_API_KEY is not set. Falling back to rule-based classification.")
        classified_jobs = []
        passed_count = 0
        failed_count = 0
        
        for job in jobs:
            title = job.get("title", "")
            desc = job.get("description", "")
            rel, scam = _rule_based_fallback(title, desc)
            
            job["ai_relevance_score"] = rel
            job["ai_scam_score"] = scam
            
            if rel >= MIN_RELEVANCE_SCORE and scam <= MAX_SCAM_SCORE:
                classified_jobs.append(job)
                passed_count += 1
            else:
                log_job_discarded(title, f"rule-based score (rel: {rel}, scam: {scam})")
                failed_count += 1
                
        log_ai_batch(len(jobs), passed_count, failed_count)
        return classified_jobs

    client = None
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.error(f"[AI_CLASSIFIER] Failed to initialize Groq client: {e}. Using fallback.")

    classified_jobs = []
    
    # Process in batches of BATCH_SIZE
    for i in range(0, len(jobs), BATCH_SIZE):
        batch = jobs[i:i+BATCH_SIZE]
        batch_results = {}
        
        if client:
            try:
                # Format jobs for Groq prompt
                formatted_jobs = []
                for index, job in enumerate(batch):
                    formatted_jobs.append({
                        "index": index,
                        "title": job.get("title", ""),
                        "company": job.get("company", ""),
                        "description": job.get("description", "")[:400]  # truncate to save tokens
                    })
                
                prompt = (
                    "You are an AI assistant that evaluates job postings for JSTP (Jamaica Student Work Program).\n"
                    "Evaluate the list of jobs and return a JSON object with a single top-level 'results' array.\n"
                    "Each item in 'results' must contain:\n"
                    "1. 'index' (int): index of job in the input.\n"
                    "2. 'relevance_score' (float, 0.0-1.0): suitable for tertiary-level students or graduates in Jamaica "
                    "(e.g., internships, entry-level, part-time, remote student jobs). Discard senior/manager roles.\n"
                    "3. 'scam_score' (float, 0.0-1.0): likelihood of being a scam, MLM, upfront payment scheme, or fake.\n\n"
                    f"Jobs to evaluate:\n{json.dumps(formatted_jobs, indent=2)}\n\n"
                    "Respond ONLY with valid JSON structure like:\n"
                    "{\n"
                    '  "results": [\n'
                    "    { \n"
                    '      "index": 0,\n'
                    '      "relevance_score": 0.85,\n'
                    '      "scam_score": 0.05\n'
                    "    }\n"
                    "  ]\n"
                    "}"
                )

                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=GROQ_MODEL,
                    response_format={"type": "json_object"},
                    timeout=20
                )
                
                response_data = json.loads(response.choices[0].message.content)
                for res in response_data.get("results", []):
                    idx = res.get("index")
                    if idx is not None and 0 <= idx < len(batch):
                        batch_results[idx] = (res.get("relevance_score", 0.0), res.get("scam_score", 0.0))
            except Exception as api_err:
                logger.error(f"[AI_CLASSIFIER] Groq API error in batch {i//BATCH_SIZE + 1}: {api_err}. Using fallback.")
                batch_results = {}

        # Sift results and apply thresholding
        passed_batch = 0
        failed_batch = 0
        for idx, job in enumerate(batch):
            title = job.get("title", "")
            desc = job.get("description", "")
            
            # Retrieve from API or fallback
            if idx in batch_results:
                rel, scam = batch_results[idx]
            else:
                rel, scam = _rule_based_fallback(title, desc)
                
            job["ai_relevance_score"] = rel
            job["ai_scam_score"] = scam
            
            if rel >= MIN_RELEVANCE_SCORE and scam <= MAX_SCAM_SCORE:
                classified_jobs.append(job)
                passed_batch += 1
            else:
                log_job_discarded(title, f"score threshold (rel: {rel}, scam: {scam})")
                failed_batch += 1
                
        log_ai_batch(len(batch), passed_batch, failed_batch)

    return classified_jobs
