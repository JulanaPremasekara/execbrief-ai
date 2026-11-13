from dataclasses import dataclass
@dataclass(frozen=True)
class Document:
    content: str
    metadata: dict

