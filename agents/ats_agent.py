from crewai import Agent
from agents.llm_config import get_llm


def create_ats_agent() -> Agent:
    return Agent(
        role="ATS Optimization Specialist",
        goal=(
            "Deliver a complete ATS improvement checklist with exactly four sections: "
            "Critical Fixes, Keyword Optimization, Formatting Fixes, and Quick Wins. "
            "Always finish all four sections — never stop mid-response."
        ),
        backstory=(
            "You are an ATS expert who knows Workday, Greenhouse, Lever, and Taleo. "
            "You give precise, numbered checklists. You always complete your full "
            "response concisely within token limits."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
        max_iter=2
    )