from crewai import LLM
from config.settings import OPENROUTER_API_KEY, MODEL_NAME, OPENROUTER_BASE_URL


def get_llm() -> LLM:
    # Pass the full model name as-is — CrewAI + OpenRouter handle it correctly
    return LLM(
        model=MODEL_NAME,
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENROUTER_API_KEY,
        temperature=0.3,
        max_tokens=4000
    )