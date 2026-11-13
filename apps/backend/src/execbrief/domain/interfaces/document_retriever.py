from typing import Protocol
from execbrief.domain.entities.document import Document
class DocumentRetriever(Protocol):
    def retrieve(self, query: str, k: int = 5) -> list[Document]: ...

