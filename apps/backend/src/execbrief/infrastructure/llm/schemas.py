from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class StrictModel(BaseModel):
    model_config=ConfigDict(extra="forbid")

class QueryPlan(StrictModel):
    operations: list[Literal["revenue","expenses","sales","turnover","projects","operations"]]=Field(max_length=6)
    retrieve: bool=True
    start: str=Field(default="2026-05",pattern=r"^2026-(05|06|07|08|09|10)$")
    end: str=Field(default="2026-10",pattern=r"^2026-(05|06|07|08|09|10)$")
    @model_validator(mode="after")
    def valid_period(self):
        if self.start>self.end or len(set(self.operations))!=len(self.operations):
            raise ValueError("Invalid plan")
        return self

class GeneratedBlock(StrictModel):
    type: Literal["text","chart"]
    content: str=Field(default="",max_length=6000)
    sources: list[str]=Field(default_factory=list,max_length=20)
    chart_type: Literal["bar","line"]|None=None
    dataset_id: str|None=None
    x: str|None=None
    y: list[str]=Field(default_factory=list,max_length=4)

class GeneratedResponse(StrictModel):
    blocks: list[GeneratedBlock]=Field(min_length=1,max_length=12)

