from execbrief.domain.analytics import OPERATIONS
class QueryPlanner:
    def __init__(self,llm): self.llm=llm
    async def plan(self,question,history):
        plan=await self.llm.generate("plan",{"question":question,"history":history,"operations":list(OPERATIONS),"reporting_period":"2026-05 through 2026-10"})
        if set(plan["operations"])-OPERATIONS.keys() or not "2026-05"<=plan["start"]<=plan["end"]<="2026-10":
            raise ValueError("Unapproved query plan")
        return plan

