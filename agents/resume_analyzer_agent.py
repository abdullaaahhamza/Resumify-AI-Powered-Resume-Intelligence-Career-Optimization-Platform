from crewai import Agent
from agents.llm_config import get_llm


def create_resume_analyzer_agent() -> Agent:
    return Agent(
        role="Expert Resume Analyzer",
        goal=(
            "Analyze a resume and deliver a complete, concise structured report "
            "with Strengths, Weaknesses, and Improvement Suggestions. "
            "Always complete the full response — never stop mid-sentence."
        ),
        backstory=(
            "You are a senior HR professional with 15+ years reviewing resumes. "
            "You give direct, specific, actionable feedback. "
            "You always finish your complete response within the token limit "
            "by being concise and structured."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )