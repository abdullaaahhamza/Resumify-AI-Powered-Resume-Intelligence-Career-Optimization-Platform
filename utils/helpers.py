import re


def score_color(score: float) -> str:
    """Return a hex color based on percentage score."""
    if score >= 80: return "#00C851"
    if score >= 60: return "#FFD700"
    if score >= 40: return "#FF8800"
    return "#FF4444"


def format_skill_badge(skill: str, status: str = "found") -> str:
    """Return HTML for a colored skill badge."""
    colors = {
        "found":      ("#00C851", "#001a00"),
        "missing":    ("#FF4444", "#1a0000"),
        "must_have":  ("#FF4444", "#1a0000"),
        "good":       ("#FFD700", "#1a1a00"),
        "bonus":      ("#00BFFF", "#001a2a"),
    }
    bg, fg = colors.get(status, ("#888888", "#111111"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:600;'
        f'margin:2px;display:inline-block;">{skill}</span>'
    )


def clean_markdown(text: str) -> str:
    """Lightly clean agent output for display."""
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def truncate(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"