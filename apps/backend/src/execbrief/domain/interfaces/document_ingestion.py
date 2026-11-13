from typing import Protocol
from pathlib import Path
from execbrief.domain.entities.document import Document
class DocumentLoader(Protocol):
    def load(self, path: Path) -> list[Document]: ...
class DocumentSplitter(Protocol):
    def split(self, documents: list[Document]) -> list[Document]: ...
class DocumentStore(Protocol):
    def replace_source(self, source: str, documents: list[Document]) -> int: ...

