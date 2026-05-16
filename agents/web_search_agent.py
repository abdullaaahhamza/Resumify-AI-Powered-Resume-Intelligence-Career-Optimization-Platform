from crewai import Agent
from crewai.tools import BaseTool
from agents.llm_config import get_llm
from duckduckgo_search import DDGS
from pydantic import BaseModel, Field
from typing import Type


class DDGSearchInput(BaseModel):
    query: str = Field(description="Search query to look up on DuckDuckGo")


class DuckDuckGoSearchTool(BaseTool):
    name: str        = "DuckDuckGo Search"
    description: str = (
        "Searches DuckDuckGo for learning resources. "
        "Input a specific search query. Returns top 4 results with titles and URLs."
    )
    args_schema: Type[BaseModel] = DDGSearchInput

    def _run(self, query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=4))
            if not results:
                return f"No results found for: {query}"
            lines = []
            for r in results:
                title = r.get("title", "No title")
                href  = r.get("href",  "No URL")
                lines.append(f"• {title} — {href}")
            return "\n".join(lines)
        except Exception as e:
            return f"Search error: {str(e)}"


def create_web_search_agent() -> Agent:
    return Agent(
        role="Learning Resources Researcher",
        goal=(
            "Find and list the best learning resources for each missing skill. "
            "Search one skill at a time and always complete resources for ALL skills."
        ),
        backstory=(
            "You are an educational researcher who finds top learning materials. "
            "You search efficiently, complete all skills, and present clean, "
            "formatted resource lists with real URLs."
        ),
        llm=get_llm(),
        tools=[DuckDuckGoSearchTool()],
        verbose=True,
        allow_delegation=False,
        max_iter=6
    )