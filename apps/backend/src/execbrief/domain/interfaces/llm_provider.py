from typing import Protocol
class LLMProvider(Protocol):
    async def generate(self, task: str, context: dict) -> dict: ...

