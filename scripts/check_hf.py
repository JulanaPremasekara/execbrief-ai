"""Opt-in hosted inference capability check; never print provider error bodies."""
import asyncio
import os
from execbrief.core import data_config
from execbrief.infrastructure.llm.huggingface_provider import HuggingFaceProvider
from execbrief.infrastructure.llm.huggingface_provider import ProviderError

async def main():
    try:
        provider=HuggingFaceProvider(os.getenv("HF_MODEL"),os.getenv("HF_TOKEN"),os.getenv("HF_PROVIDER","auto"))
        result=await provider.generate("plan",{"question":"Show monthly revenue trends.","operations":["revenue"],"reporting_period":"2026-05 through 2026-10"})
        assert "revenue" in result["operations"]
        print("Hosted model structured planning capability verified.")
    except ProviderError as error:
        print("Hosted capability check failed:", str(error))
        return 1
    except Exception as error:
        print("Hosted configuration check failed:", type(error).__name__)
        return 1
    return 0
if __name__=="__main__":
    raise SystemExit(asyncio.run(main()))
