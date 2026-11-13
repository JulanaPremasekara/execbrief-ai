from typing import Protocol
from execbrief.domain.entities.response_block import Block

class ResponseProvider(Protocol):
    def respond(self, question: str, history: list[dict]) -> list[Block]: ...

