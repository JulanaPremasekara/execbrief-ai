import json
import pandas as pd
from execbrief.domain.analytics import OPERATIONS
from execbrief.domain.interfaces.metrics_repository import MetricsRepository

class PandasAnalytics:
    def __init__(self, repository: MetricsRepository):
        self.repository=repository

    def calculate(self,operation,start,end):
        if operation not in OPERATIONS:
            raise ValueError("Unsupported analytical operation")
        table,x,ys=OPERATIONS[operation]
        frame=pd.DataFrame(self.repository.fetch(table))
        if frame.empty:
            rows=[]
        else:
            frame=frame[(frame.month>=start)&(frame.month<=end)].copy()
            if operation=="revenue":
                frame=frame.sort_values("month")
                prior=frame.actual_revenue.shift(1)
                frame["growth_percent"]=((frame.actual_revenue-prior)/prior.where(prior!=0)*100).round(2)
                frame["variance"]=frame.actual_revenue-frame.target_revenue
            elif operation in ("expenses","sales"):
                group="department" if operation=="expenses" else "month"
                actual,target=("actual_expenses","budget") if operation=="expenses" else ("revenue","target")
                frame=frame.groupby(group,as_index=False)[[actual,target]].sum()
                frame["variance"]=frame[actual]-frame[target]
            elif operation=="turnover":
                frame=frame.groupby("month",as_index=False)[["departures","opening_headcount","closing_headcount"]].sum()
                denominator=(frame.opening_headcount+frame.closing_headcount)/2
                frame["turnover_percent"]=(frame.departures/denominator.where(denominator!=0)*100).round(2)
            elif operation=="projects":
                frame=frame[frame.month==frame.month.max()]
                frame=frame.groupby("project",as_index=False).delay_days.max()
            else:
                frame=frame.groupby("month",as_index=False)[["sla_percent","target_percent"]].mean()
                frame["variance"]=frame.sla_percent-frame.target_percent
            rows=json.loads(frame[[x,*ys]].to_json(orient="records"))
        return {"id":operation,"columns":[x,*ys],"rows":rows,
                "units":"percent" if operation in ("turnover","operations") else "days" if operation=="projects" else "LKR",
                "period":{"start":start,"end":end}}

