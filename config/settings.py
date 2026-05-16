import os
from dotenv import load_dotenv

load_dotenv()

# ── API Configuration ────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "openrouter/openai/gpt-oss-120b:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ── Semantic Matching ────────────────────────────────────────────────────────
SEMANTIC_THRESHOLD = 0.42   # Cosine similarity cutoff for skill match (0–1)

# ── ATS Score Weights (must sum to 100) ─────────────────────────────────────
ATS_WEIGHTS = {
    "contact_info":    15,
    "section_headers": 20,
    "bullet_points":   15,
    "file_format":     10,
    "length":          10,
    "no_tables":       10,
    "keywords":        10,
    "dates_format":    10,
}

# ── Section Detection Keywords ───────────────────────────────────────────────
SECTION_KEYWORDS = [
    "summary", "objective", "profile", "about",
    "experience", "work experience", "employment", "work history",
    "education", "academic", "qualifications",
    "skills", "technical skills", "competencies",
    "projects", "certifications", "achievements",
    "awards", "languages", "interests", "references",
    "publications", "volunteer", "leadership"
]

# ── Upload Directory ─────────────────────────────────────────────────────────
UPLOAD_DIR = "uploads"