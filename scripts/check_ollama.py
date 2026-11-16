"""Manual local inference check; does not connect to Supabase."""
import asyncio
import os

from execbrief.core.container import build_llm


async def main():
    os.environ["LLM_PROVIDER"] = "local"
    try:
        provider = build_llm()
        plan = await provider.generate("plan", {"question": "Show revenue trends", "operations": ["revenue"], "reporting_period": "2026-05 through 2026-10"})
        if plan["operations"] != ["revenue"]:
            raise ValueError("Unexpected planning result")
        await provider.generate("response", {"question": "Explain the evidence", "evidence": {"e1": {"id": "e1", "content": "Fictional company report is available."}}, "datasets": {}})
        print("Ollama planning and response schemas verified. Full RAG grounding is not tested.")
        return 0
    except Exception as error:
        print("Ollama check failed:", type(error).__name__)
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
