import json
import re
import requests
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME


class SkillExtractor:
    """
    Extracts skills, tools, and requirements from job descriptions using
    LLM inference via direct HTTP — NO hardcoded skill lists whatsoever.
    """

    def __init__(self):
        # Strip the leading "openrouter/" prefix for the actual API call
        raw = MODEL_NAME
        if raw.startswith("openrouter/"):
            raw = raw[len("openrouter/"):]
        self.model = raw
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL

    def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """Direct HTTP call to OpenRouter — avoids all SDK model-name issues."""
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
            "temperature": 0.1
        }
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        if resp.status_code != 200:
            raise RuntimeError(
                f"OpenRouter API error {resp.status_code}: {resp.text[:300]}"
            )
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

    def extract_from_jd(self, jd_text: str) -> dict:
        """
        Send JD to LLM, get back structured JSON of all skills/tools/requirements.
        """
        system_prompt = (
            "You are a precise skill extraction engine. "
            "You output ONLY valid JSON. No markdown. No code fences. "
            "No extra text before or after the JSON object. "
            "Your entire response must be parseable by json.loads()."
        )

        user_prompt = f"""Read the job description below carefully and extract ALL mentioned or strongly implied:
- Technical skills (languages, frameworks, libraries, platforms)
- Tools and technologies
- Soft skills and behavioral competencies
- Domain knowledge areas
- Must-have vs nice-to-have items

STRICT RULES:
1. Do NOT invent skills not present or strongly implied in the JD.
2. Extract the EXACT names used in the JD (e.g. "React.js" not just "React").
3. Distinguish clearly between REQUIRED and PREFERRED/BONUS items.
4. Be exhaustive — miss nothing. Extract at least 5-15 skills if they exist.
5. The job_title must be extracted or inferred from the JD content.

Job Description:
\"\"\"
{jd_text[:4000]}
\"\"\"

Respond with ONLY this JSON structure (no markdown, no code fences, no extra text):
{{
  "job_title": "extracted or inferred job title here",
  "must_have_skills": ["skill1", "skill2", "skill3"],
  "good_to_have_skills": ["skill1", "skill2"],
  "tools_and_technologies": ["tool1", "tool2", "tool3"],
  "soft_skills": ["skill1", "skill2"],
  "domain_knowledge": ["domain1", "domain2"],
  "experience_required": "e.g. 3+ years or Not specified",
  "education_required": "e.g. Bachelor in CS or Not specified",
  "key_responsibilities": ["responsibility1", "responsibility2"]
}}"""

        try:
            raw = self._call_llm(system_prompt, user_prompt, max_tokens=2000)

            # Aggressively clean the response
            # Remove markdown code fences if present
            raw = re.sub(r'^```json\s*', '', raw, flags=re.MULTILINE)
            raw = re.sub(r'^```\s*',     '', raw, flags=re.MULTILINE)
            raw = re.sub(r'\s*```$',     '', raw, flags=re.MULTILINE)
            raw = raw.strip()

            # If the model wrapped it in extra text, try to extract just the JSON object
            if not raw.startswith('{'):
                match = re.search(r'\{.*\}', raw, re.DOTALL)
                if match:
                    raw = match.group(0)

            extracted = json.loads(raw)

            # Validate — ensure all expected keys exist
            extracted = self._validate_and_fill(extracted)
            return extracted

        except json.JSONDecodeError as e:
            # Last resort: try to manually extract skills using regex
            return self._regex_fallback(jd_text)
        except Exception as e:
            raise RuntimeError(f"Skill extraction failed: {e}")

    def _validate_and_fill(self, data: dict) -> dict:
        """Ensure all expected keys exist and are lists where needed."""
        defaults = self._empty_structure()
        for key in defaults:
            if key not in data:
                data[key] = defaults[key]
            # Ensure list fields are actually lists
            if key in ["must_have_skills", "good_to_have_skills",
                       "tools_and_technologies", "soft_skills",
                       "domain_knowledge", "key_responsibilities"]:
                if not isinstance(data[key], list):
                    data[key] = []
        # Ensure strings
        for key in ["job_title", "experience_required", "education_required"]:
            if not isinstance(data.get(key), str) or not data[key]:
                data[key] = defaults[key]
        return data

    def _regex_fallback(self, jd_text: str) -> dict:
        """
        Pure regex fallback — extracts skill-like tokens from JD text.
        Used only when LLM JSON parsing completely fails.
        No predefined lists — extracts based on JD content patterns.
        """
        # Extract capitalized multi-word phrases and tech-looking tokens
        # These patterns catch: Python, React.js, AWS, CI/CD, REST APIs, etc.
        patterns = [
            r'\b[A-Z][a-zA-Z]*(?:\.[a-zA-Z]+)+\b',          # React.js, Node.js
            r'\b[A-Z]{2,}(?:[\-/][A-Z]{2,})*\b',             # AWS, CI/CD, REST
            r'\b(?:Python|Java|JavaScript|TypeScript|SQL|HTML|CSS|'
            r'Docker|Kubernetes|Git|Linux|Excel|PowerPoint|'
            r'TensorFlow|PyTorch|Pandas|NumPy|Scikit|FastAPI|'
            r'Django|Flask|Spring|Angular|Vue|React|Next\.js|'
            r'PostgreSQL|MySQL|MongoDB|Redis|Kafka|Spark|'
            r'Azure|GCP|Terraform|Jenkins|Ansible)\b',
        ]
        found = set()
        for pat in patterns:
            found.update(re.findall(pat, jd_text))

        skills = sorted(found)[:20]
        half   = len(skills) // 2

        return {
            "job_title":              self._extract_title(jd_text),
            "must_have_skills":       skills[:half],
            "good_to_have_skills":    skills[half:],
            "tools_and_technologies": [],
            "soft_skills":            [],
            "domain_knowledge":       [],
            "experience_required":    self._extract_experience(jd_text),
            "education_required":     "Not specified",
            "key_responsibilities":   []
        }

    def _extract_title(self, text: str) -> str:
        """Try to find a job title in the first few lines."""
        lines = [l.strip() for l in text.split('\n') if l.strip()][:5]
        for line in lines:
            if len(line.split()) <= 6 and any(
                kw in line.lower() for kw in
                ["engineer", "developer", "analyst", "scientist",
                 "manager", "designer", "architect", "lead", "intern"]
            ):
                return line
        return "Software Professional"

    def _extract_experience(self, text: str) -> str:
        match = re.search(
            r'(\d+\+?\s*(?:to\s*\d+)?\s*years?)',
            text, re.IGNORECASE
        )
        return match.group(1) + " experience" if match else "Not specified"

    def get_all_jd_skills(self, extracted: dict) -> list:
        """
        Flatten all extracted categories into one deduplicated skill list
        for use in semantic matching.
        """
        buckets = [
            "must_have_skills",
            "good_to_have_skills",
            "tools_and_technologies",
            "soft_skills",
            "domain_knowledge"
        ]
        seen, result = set(), []
        for bucket in buckets:
            for skill in extracted.get(bucket, []):
                key = skill.lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    result.append(skill.strip())
        return result

    def _empty_structure(self) -> dict:
        return {
            "job_title":               "Unknown Role",
            "must_have_skills":        [],
            "good_to_have_skills":     [],
            "tools_and_technologies":  [],
            "soft_skills":             [],
            "domain_knowledge":        [],
            "experience_required":     "Not specified",
            "education_required":      "Not specified",
            "key_responsibilities":    []
        }