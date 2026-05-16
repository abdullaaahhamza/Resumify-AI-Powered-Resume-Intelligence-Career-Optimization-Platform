import re
from config.settings import SECTION_KEYWORDS


class TextPreprocessor:
    """Cleans, normalizes, and splits resume/JD text into sections."""

    # ── Main Entry Points ────────────────────────────────────────────────────
    def preprocess(self, raw_text: str) -> dict:
        cleaned    = self._clean(raw_text)
        normalized = self._normalize(cleaned)
        sections   = self._extract_sections(normalized)
        return {
            "cleaned_text":    cleaned,
            "normalized_text": normalized,
            "sections":        sections
        }

    def preprocess_jd(self, raw_text: str) -> dict:
        cleaned    = self._clean(raw_text)
        normalized = self._normalize(cleaned)
        return {
            "cleaned_text":    cleaned,
            "normalized_text": normalized,
            "full_text":       normalized
        }

    # ── Cleaning ─────────────────────────────────────────────────────────────
    def _clean(self, text: str) -> str:
        # Drop non-ASCII noise
        text = text.encode("ascii", "ignore").decode("ascii")
        # Collapse 3+ blank lines → 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Collapse multiple spaces/tabs → single space
        text = re.sub(r'[ \t]{2,}', ' ', text)
        # Remove invisible control characters
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        return text.strip()

    def _normalize(self, text: str) -> str:
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        return '\n'.join(lines)

    # ── Section Detector ─────────────────────────────────────────────────────
    def _extract_sections(self, text: str) -> dict:
        sections: dict = {}
        current_section = "header"
        current_content: list = []

        for line in text.split('\n'):
            lower = line.lower().strip()
            matched = None

            for keyword in SECTION_KEYWORDS:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                # Treat as header only if the line is short (not a sentence)
                if re.search(pattern, lower) and len(line.split()) <= 6:
                    matched = keyword
                    break

            if matched:
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = matched
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return sections