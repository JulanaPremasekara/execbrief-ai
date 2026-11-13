from execbrief.domain.entities.response_block import Block

class MockResponseProvider:
    def respond(self, question: str, history: list[dict]) -> list[Block]:
        revenue = {"id": "monthly_revenue", "columns": ["month", "actual", "target"], "units": "LKR millions",
                   "rows": [dict(month=m, actual=a, target=t) for m,a,t in
                            zip(["May","Jun","Jul","Aug","Sep","Oct"], [12,13,14,15,16,14], [13,13,14,15,16,16])]}
        expenses = {"id": "department_expenses", "columns": ["department", "actual", "budget"], "units": "LKR millions",
                    "rows": [dict(department=d, actual=a, budget=b) for d,a,b in
                             zip(["Finance","Sales","HR","Operations","IT"], [1,2,1,4,2], [1,2,1,3,2])]}
        def chart(id, kind, title, data, x, y):
            return Block(id, "chart", spec=dict(id=id, type="chart", chart_type=kind, title=title,
                         dataset_id=data["id"], x=x, y=y), dataset=data)
        blocks = [
            Block("b1", "text", "Fictional Nexora briefing: October revenue was LKR 14 million, down from LKR 16 million in September."),
            chart("b2", "line", "Revenue against target", revenue, "month", ["actual","target"]),
            Block("b3", "text", "Operations expenses exceeded the illustrative budget by LKR 1 million. These fixtures do not establish the cause of the revenue decline."),
            chart("b4", "bar", "October departmental expenses", expenses, "department", ["actual","budget"]),
            Block("b5", "text", "Recommendations: Review the October sales pipeline and investigate the Operations budget variance before deciding on corrective action.")]
        return [b for b in blocks if b.type == "text"] if "text only" in question.lower() else blocks

