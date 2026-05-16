import json
import re
import requests
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME


class GapAnalyzer:
    """
    Classifies missing skills into Must Have / Good to Have / Bonus
    using LLM context — no predefined rules.
    """

    def __init__(self):
        raw = MODEL_NAME
        if raw.startswith("openrouter/"):
            raw = raw[len("openrouter/"):]
        self.model   = raw
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 1200) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://resumify.app",
            "X-Title": "Resumify - Your Job Mate"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2
        }
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        if resp.status_code != 200:
            raise RuntimeError(f"OpenRouter API error {resp.status_code}: {resp.text[:300]}")
        return resp.json()["choices"][0]["message"]["content"].strip()

    def analyze(self, missing_skills: list, jd_extracted: dict, resume_text: str) -> dict:
        if not missing_skills:
            return {
                "must_have":    [],
                "good_to_have": [],
                "bonus":        [],
                "summary":      "🎉 Your resume covers all detected skills for this role!"
            }

        job_title        = jd_extracted.get("job_title", "the role")
        must_in_jd       = jd_extracted.get("must_have_skills", [])
        responsibilities = jd_extracted.get("key_responsibilities", [])

        system_prompt = (
            "You are a precise career analyst. "
            "Return ONLY valid JSON. No markdown. No code fences. No extra text."
        )

        user_prompt = f"""A candidate is applying for: {job_title}

Skills MISSING from their resume (found in JD but not in resume):
{json.dumps(missing_skills, indent=2)}

JD explicitly marked these as required/must-have:
{json.dumps(must_in_jd, indent=2)}

Key responsibilities:
{json.dumps(responsibilities[:6], indent=2)}

Classify EVERY missing skill into exactly one category:
- "must_have": application will likely be rejected without this
- "good_to_have": competitive advantage, learn after must-haves
- "bonus": nice-to-have differentiator

EVERY skill from the missing list must appear in exactly one category. Do not drop any.

Return ONLY this JSON (no markdown, no extra text):
{{
  "must_have": ["skill", ...],
  "good_to_have": ["skill", ...],
  "bonus": ["skill", ...],
  "summary": "One sentence describing the overall skill gap situation."
}}"""

        try:
            raw = self._call_llm(system_prompt, user_prompt)
            raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'^```\s*',     '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$',     '', raw, flags=re.MULTILINE)
            raw = raw.strip()

            if not raw.startswith('{'):
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    raw = match.group(0)

            result = json.loads(raw)

            # Validate all keys exist
            for key in ["must_have", "good_to_have", "bonus", "summary"]:
                if key not in result:
                    result[key] = [] if key != "summary" else ""

            return result

        except Exception:
            # Safe fallback: classify using JD must-have list
            jd_must = {s.lower() for s in must_in_jd}
            must  = [s for s in missing_skills if s.lower() in jd_must]
            rest  = [s for s in missing_skills if s.lower() not in jd_must]
            mid   = max(1, len(rest) // 2)
            return {
                "must_have":    must or missing_skills[:max(1, len(missing_skills)//3)],
                "good_to_have": rest[:mid],
                "bonus":        rest[mid:],
                "summary":      f"You are missing {len(missing_skills)} skills needed for {job_title}."
            }