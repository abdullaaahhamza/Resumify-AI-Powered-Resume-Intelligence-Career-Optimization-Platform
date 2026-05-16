import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import SEMANTIC_THRESHOLD


class SemanticMatcher:
    """
    Matches every JD-extracted skill against the resume using
    sentence-transformer embeddings + cosine similarity.
    Zero predefined lists — pure vector math.
    """

    _model = None   # class-level cache so we load only once per session

    def __init__(self):
        if SemanticMatcher._model is None:
            print("⏳ Loading semantic model (first run only)…")
            SemanticMatcher._model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Semantic model ready.")
        self.model = SemanticMatcher._model

    # ── Public API ───────────────────────────────────────────────────────────
    def match(self, resume_text: str, jd_skills: list) -> dict:
        """
        For each skill extracted from the JD, check if the resume
        contains it (semantically). Returns a structured result dict.
        """
        if not jd_skills:
            return self._empty_result()

        chunks            = self._chunk(resume_text)
        resume_embeddings = self.model.encode(chunks, show_progress_bar=False,
                                              batch_size=32)
        found, missing, scores = [], [], {}

        for skill in jd_skills:
            skill_emb = self.model.encode([skill], show_progress_bar=False)
            sims      = cosine_similarity(skill_emb, resume_embeddings)[0]
            best      = float(np.max(sims))
            scores[skill] = round(best, 3)

            if best >= SEMANTIC_THRESHOLD:
                found.append(skill)
            else:
                missing.append(skill)

        total   = len(jd_skills)
        matched = len(found)
        pct     = round((matched / total) * 100, 1) if total else 0

        return {
            "overall_score":    pct,
            "found_skills":     found,
            "missing_skills":   missing,
            "skill_scores":     scores,
            "total_jd_skills":  total,
            "matched_count":    matched
        }

    def overall_similarity(self, resume_text: str, jd_text: str) -> float:
        """High-level document-level cosine similarity (0–100)."""
        r_emb = self.model.encode([resume_text[:3000]], show_progress_bar=False)
        j_emb = self.model.encode([jd_text[:3000]],    show_progress_bar=False)
        sim   = cosine_similarity(r_emb, j_emb)[0][0]
        return round(float(sim) * 100, 1)

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _chunk(self, text: str, size: int = 150, overlap: int = 50) -> list:
        words = text.split()
        step  = size - overlap
        chunks = [
            ' '.join(words[i:i + size])
            for i in range(0, len(words), step)
            if words[i:i + size]
        ]
        return chunks or [text]

    def _empty_result(self) -> dict:
        return {
            "overall_score":   0,
            "found_skills":    [],
            "missing_skills":  [],
            "skill_scores":    {},
            "total_jd_skills": 0,
            "matched_count":   0
        }