"""Opt-in selected-provider check. Never print credentials or response bodies."""
import asyncio
from execbrief.core.container import build_llm
from execbrief.infrastructure.llm.google_provider import GoogleProviderError

async def main():
    try:
        result = await build_llm().generate("plan", {"question": "Show revenue trends", "operations": ["revenue"], "reporting_period": "2026-05 through 2026-10"})
        assert "revenue" in result["operations"]
        print("Selected hosted provider structured planning verified.")
        return 0
    except GoogleProviderError as error:
        print("Provider check failed:", str(error))
        return 1
    except Exception as error:
        print("Provider configuration failed:", type(error).__name__)
        return 1

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
