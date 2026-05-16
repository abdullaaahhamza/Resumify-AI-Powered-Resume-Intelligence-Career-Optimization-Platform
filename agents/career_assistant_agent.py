from crewai import Agent
from agents.llm_config import get_llm


def create_career_assistant_agent() -> Agent:
    return Agent(
        role="Career Development Strategist",
        goal=(
            "Build a complete 3-phase learning roadmap covering all missing skills. "
            "Always finish all phases and the daily practice plan — never cut off."
        ),
        backstory=(
            "You are an elite career coach who creates realistic, week-by-week plans. "
            "You are concise, specific, and always complete your full roadmap "
            "within token limits by being direct."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )