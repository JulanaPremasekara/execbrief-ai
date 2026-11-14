import asyncio
import pytest
from execbrief.infrastructure.data.synthetic import facts
from execbrief.infrastructure.analytics.pandas_engine import PandasAnalytics
from execbrief.application.use_cases.ask_grounded import AskGroundedUseCase
from execbrief.application.services.response_planner import ResponsePlanner
from execbrief.infrastructure.llm.schemas import QueryPlan,GeneratedResponse
from execbrief.domain.entities.document import Document

class Repository:
    def fetch(self,dataset): return facts()[dataset]
class Retriever:
    def retrieve(self,query): return [Document("Atlas acceptance was deferred.",{"filename":"Minutes.pdf"})]
class LLM:
    async def generate(self,task,context):
        if task=="plan":
            return QueryPlan(operations=["revenue","expenses","sales","turnover","projects","operations"]).model_dump()
        data=context["datasets"]["revenue"]
        evidence=context["evidence"]
        key=next(iter(evidence))
        return GeneratedResponse(blocks=[
            {"type":"text","content":evidence[key]["content"],"sources":[key]},
            {"type":"chart","chart_type":"line","dataset_id":"revenue","x":"month","y":["actual_revenue","target_revenue"]},
            {"type":"text","content":"Recommendation: Review delivery milestones.","sources":["evidence:0"]}
        ]).model_dump()

QUESTIONS=["How is our company performing?","Show revenue trends over the last six months.",
 "Compare departmental expenses.","Which departments are underperforming?",
 "Why did revenue decline in October?","What are our biggest operational risks?",
 "How has employee turnover changed?","Which projects are delayed?",
 "What management decisions require attention?","Compare actual performance against targets."]

@pytest.mark.parametrize("question",QUESTIONS)
def test_complete_workflow(question):
    async def run():
        return [event async for event in AskGroundedUseCase(LLM(),PandasAnalytics(Repository()),Retriever()).execute(question,[])]
    events=asyncio.run(run())
    assert events[-1][0]=="done"
    chart=next(p for e,p in events if e=="chart")
    assert chart["dataset"]["rows"][-1]["actual_revenue"]==14000000
    assert events[-1][1]["stream_mode"]=="validated_blocks"

def test_calculations():
    engine=PandasAnalytics(Repository())
    revenue=engine.calculate("revenue","2026-05","2026-10")["rows"]
    assert revenue[0]["growth_percent"] is None
    assert revenue[-1]["growth_percent"]==-12.5
    assert revenue[-1]["variance"]==-2000000
    projects=engine.calculate("projects","2026-05","2026-10")["rows"]
    assert next(r for r in projects if r["project"]=="Atlas")["delay_days"]==14
    expenses=engine.calculate("expenses","2026-10","2026-10")["rows"]
    assert next(r for r in expenses if r["department"]=="Operations")["variance"]==1000000
    sales=engine.calculate("sales","2026-10","2026-10")["rows"][0]
    assert sales["revenue"]==14000000 and sales["variance"]==-2000000
    source=facts()["employee_turnover"]
    expected=round(sum(r["departures"] for r in source if r["month"]=="2026-10")/150*100,2)
    assert engine.calculate("turnover","2026-10","2026-10")["rows"][0]["turnover_percent"]==expected
    operational=engine.calculate("operations","2026-10","2026-10")["rows"][0]
    assert operational["target_percent"]==95

def test_zero_denominators_and_empty_data():
    class Zero:
        def fetch(self,dataset):
            if dataset=="monthly_revenue":
                return [{"month":"2026-05","actual_revenue":0,"target_revenue":0},{"month":"2026-06","actual_revenue":10,"target_revenue":10}]
            return []
    engine=PandasAnalytics(Zero())
    assert engine.calculate("revenue","2026-05","2026-06")["rows"][1]["growth_percent"] is None
    assert engine.calculate("turnover","2026-05","2026-06")["rows"]==[]

def test_invented_numbers_rejected():
    with pytest.raises(ValueError):
        ResponsePlanner().resolve({"blocks":[{"type":"text","content":"Revenue is 999999","sources":["a"]}]},{},{"a":{"content":"Revenue is 14"}})

def test_arbitrary_operations_rejected():
    with pytest.raises(ValueError):
        QueryPlan(operations=["DROP TABLE"])
    with pytest.raises(ValueError):
        PandasAnalytics(Repository()).calculate("SELECT *","2026-05","2026-10")

def test_missing_evidence():
    class EmptyLLM:
        async def generate(self,*args): return {"operations":[],"retrieve":False,"start":"2026-05","end":"2026-10"}
    async def run():
        return [e async for e in AskGroundedUseCase(EmptyLLM(),None,None).execute("question",[])]
    events=asyncio.run(run())
    assert "Insufficient evidence" in next(p["delta"] for e,p in events if e=="text_delta")
