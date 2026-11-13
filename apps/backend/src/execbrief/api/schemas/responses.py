from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, model_validator

class TextBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["text"]
    content: str

class ChartBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["chart"]
    chart_type: Literal["bar", "line"]
    title: str
    dataset_id: str
    x: str
    y: list[str] = Field(min_length=1)

class ChartPayload(BaseModel):
    block_id: str
    spec: ChartBlock
    dataset: dict

    @model_validator(mode="after")
    def approved_dataset(self):
        allowed = {"monthly_revenue": {"month","actual","target"},
                   "department_expenses": {"department","actual","budget"}}
        spec = self.spec
        columns = allowed.get(spec.dataset_id, set())
        if (spec.id != self.block_id or self.dataset.get("id") != spec.dataset_id
            or spec.x not in columns or not set(spec.y) <= columns
            or set(self.dataset.get("columns", [])) != columns):
            raise ValueError("Unapproved chart dataset or columns")
        for row in self.dataset.get("rows", []):
            if not columns <= row.keys() or any(type(row[y]) not in (int, float) for y in spec.y):
                raise ValueError("Invalid chart rows")
        return self

