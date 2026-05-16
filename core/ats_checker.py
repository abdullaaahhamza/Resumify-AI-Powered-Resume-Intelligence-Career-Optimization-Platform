import re
from config.settings import ATS_WEIGHTS, SECTION_KEYWORDS


class ATSChecker:
    """
    Scores a resume on ATS friendliness across 8 criteria.
    Maximum score = 100.
    """

    def analyze(self, raw_text: str, file_format: str, sections: dict) -> dict:
        score     = 0
        issues    = []
        breakdown = {}

        checks = [
            ("contact_info",    self._check_contact(raw_text)),
            ("section_headers", self._check_sections(sections)),
            ("bullet_points",   self._check_bullets(raw_text)),
            ("file_format",     self._check_format(file_format)),
            ("length",          self._check_length(raw_text)),
            ("no_tables",       self._check_tables(raw_text)),
            ("keywords",        self._check_keywords(raw_text)),
            ("dates_format",    self._check_dates(raw_text)),
        ]

        for key, (pts, found_issues) in checks:
            breakdown[key] = pts
            score += pts
            issues.extend(found_issues)

        total = min(score, 100)
        return {
            "total_score": total,
            "breakdown":   breakdown,
            "issues":      issues,
            "suggestions": self._suggestions(issues),
            "grade":       self._grade(total)
        }

    # ── Individual Checks ────────────────────────────────────────────────────
    def _check_contact(self, text):
        pts    = ATS_WEIGHTS["contact_info"]
        issues = []
        ded    = 0

        if not re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text):
            issues.append("❌ Email address not detected")
            ded += 6
        if not re.search(r'(\+?\d[\d\s\-\(\)]{7,15}\d)', text):
            issues.append("❌ Phone number not detected or poorly formatted")
            ded += 5
        if not re.search(r'linkedin\.com', text, re.IGNORECASE):
            issues.append("⚠️ LinkedIn profile URL not found")
            ded += 4

        return max(0, pts - ded), issues

    def _check_sections(self, sections):
        pts      = ATS_WEIGHTS["section_headers"]
        issues   = []
        ded      = 0
        required = ["experience", "education", "skills"]

        for req in required:
            found = any(req in s.lower() for s in sections)
            if not found:
                issues.append(f"❌ Standard section missing: '{req.title()}'")
                ded += 6

        return max(0, pts - ded), issues

    def _check_bullets(self, text):
        pts      = ATS_WEIGHTS["bullet_points"]
        issues   = []
        patterns = [r'^\s*[-•*▪▸►●]\s', r'^\s*\d+\.\s']
        count    = sum(
            1 for line in text.split('\n')
            if any(re.match(p, line) for p in patterns)
        )

        if count < 5:
            issues.append("⚠️ Very few bullet points found. Use bullets for experience/skills.")
            return max(0, pts - 12), issues
        elif count < 10:
            issues.append("⚠️ More bullet points recommended for better ATS readability.")
            return max(0, pts - 5), issues

        return pts, issues

    def _check_format(self, fmt):
        pts    = ATS_WEIGHTS["file_format"]
        issues = []

        if fmt.upper() in ["PDF", "DOCX"]:
            return pts, issues
        issues.append(f"❌ Format '{fmt}' may not be ATS-compatible. Use PDF or DOCX.")
        return 0, issues

    def _check_length(self, text):
        pts    = ATS_WEIGHTS["length"]
        issues = []
        words  = len(text.split())

        if words < 200:
            issues.append("⚠️ Resume too short (< 200 words). Expand your descriptions.")
            return max(0, pts - 8), issues
        elif words > 1200:
            issues.append("⚠️ Resume too long (> 1200 words). Aim for 1–2 pages.")
            return max(0, pts - 4), issues

        return pts, issues

    def _check_tables(self, text):
        pts    = ATS_WEIGHTS["no_tables"]
        issues = []

        if text.count('|') > 10:
            issues.append("⚠️ Table/column layout detected. ATS may misparse tables.")
            return max(0, pts - 8), issues

        return pts, issues

    def _check_keywords(self, text):
        pts    = ATS_WEIGHTS["keywords"]
        issues = []
        lower  = text.lower()

        if not any(kw in lower for kw in ["skills", "technologies", "tools", "proficient", "expertise"]):
            issues.append("⚠️ No Skills/Technologies section keyword detected.")
            return max(0, pts - 8), issues

        return pts, issues

    def _check_dates(self, text):
        pts      = ATS_WEIGHTS["dates_format"]
        issues   = []
        patterns = [
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}\b',
            r'\b\d{4}\s*[-–]\s*(\d{4}|Present|Current|Now)\b',
            r'\b\d{2}/\d{4}\b'
        ]
        found = any(re.search(p, text, re.IGNORECASE) for p in patterns)

        if not found:
            issues.append("⚠️ No clear date formatting found. Use 'Jan 2022 – Present'.")
            return max(0, pts - 8), issues

        return pts, issues

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _suggestions(self, issues: list) -> list:
        mp = {
            "Email":    "Add a professional email at the top (e.g. name@gmail.com).",
            "Phone":    "Include phone in format: +1 (555) 123-4567.",
            "LinkedIn": "Add your LinkedIn URL: linkedin.com/in/yourname.",
            "section":  "Add clear section headers: Experience, Education, Skills.",
            "bullet":   "Use bullet points (•) for experience and achievements.",
            "table":    "Replace table/column layouts with a single-column format.",
            "date":     "Format dates consistently: 'Month Year – Month Year'.",
            "short":    "Add more detail to your experience and skills sections.",
            "long":     "Trim to 1–2 pages; focus on the most relevant experience.",
        }
        result = []
        for issue in issues:
            for key, suggestion in mp.items():
                if key.lower() in issue.lower():
                    result.append(suggestion)
        return list(dict.fromkeys(result))   # deduplicate, preserve order

    def _grade(self, score: int) -> str:
        if score >= 85: return "Excellent ✅"
        if score >= 70: return "Good 👍"
        if score >= 55: return "Average ⚠️"
        return "Needs Improvement ❌"