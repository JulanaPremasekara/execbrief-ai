from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

class HistoryEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=10000)

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    question: str = Field(min_length=1, max_length=2000)
    history: list[HistoryEntry] = Field(default_factory=list, max_length=20)

