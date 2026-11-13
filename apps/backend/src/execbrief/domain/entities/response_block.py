from dataclasses import dataclass, field

@dataclass(frozen=True)
class Block:
    id: str
    type: str
    content: str = ""
    spec: dict = field(default_factory=dict)
    dataset: dict = field(default_factory=dict)

