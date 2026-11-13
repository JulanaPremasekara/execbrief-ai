import csv
import random
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

DEPARTMENTS = ["Finance", "Sales", "Human Resources", "Operations", "IT"]
SCHEMAS = {
 "monthly_revenue": {"month":str,"actual_revenue":int,"target_revenue":int},
 "department_expenses": {"month":str,"department":str,"actual_expenses":int,"budget":int},
 "sales_performance": {"month":str,"channel":str,"revenue":int,"target":int},
 "employee_turnover": {"month":str,"department":str,"opening_headcount":int,"hires":int,"departures":int,"closing_headcount":int},
 "project_performance": {"month":str,"project":str,"planned_days":int,"actual_days":int,"delay_days":int},
 "operational_kpis": {"month":str,"department":str,"sla_percent":int,"target_percent":int}
}
KEYS = {"monthly_revenue":["month"],"department_expenses":["month","department"],
 "sales_performance":["month","channel"],"employee_turnover":["month","department"],
 "project_performance":["month","project"],"operational_kpis":["month","department"]}
REPORTS = {"Financial Performance Report":"monthly_revenue","Sales Performance Report":"sales_performance",
 "HR Performance Report":"employee_turnover","Operations Report":"operational_kpis",
 "Management Meeting Minutes":"project_performance","Business Risk Register":"department_expenses"}

def facts(seed=2026):
    rng = random.Random(seed)
    result = {name:[] for name in SCHEMAS}
    headcounts = dict(zip(DEPARTMENTS,[20,35,10,60,25]))
    for i, month in enumerate([f"2026-{m:02d}" for m in range(5,11)]):
        revenue = [12000000,13000000,14000000,15000000,16000000,14000000][i]
        target = [13000000,13000000,14000000,15000000,16000000,16000000][i]
        result["monthly_revenue"].append(dict(month=month,actual_revenue=revenue,target_revenue=target))
        for channel, share in [("Existing clients",60),("New clients",40)]:
            result["sales_performance"].append(dict(month=month,channel=channel,revenue=revenue*share//100,target=target*share//100))
        for department,budget in zip(DEPARTMENTS,[1000000,2000000,1000000,3000000,2000000]):
            actual = budget + (1000000 if i==5 and department=="Operations" else rng.randint(-5,5)*10000)
            result["department_expenses"].append(dict(month=month,department=department,actual_expenses=actual,budget=budget))
            departures = rng.randint(0,2)
            opening = headcounts[department]
            result["employee_turnover"].append(dict(month=month,department=department,opening_headcount=opening,hires=departures,departures=departures,closing_headcount=opening))
            result["operational_kpis"].append(dict(month=month,department=department,sla_percent=90 if i==5 and department=="Operations" else rng.randint(95,99),target_percent=95))
        for project in ["Atlas","Beacon","Cedar"]:
            delay = 14 if i==5 and project=="Atlas" else 0
            result["project_performance"].append(dict(month=month,project=project,planned_days=30,actual_days=30+delay,delay_days=delay))
    return result

def generate(root: Path, seed=2026):
    data = facts(seed)
    for folder in ["csv","pdf"]:
        (root/folder).mkdir(parents=True,exist_ok=True)
    for name,rows in data.items():
        with (root/"csv"/f"{name}.csv").open("w",newline="",encoding="utf-8") as stream:
            writer=csv.DictWriter(stream,fieldnames=[*SCHEMAS[name],"fictional"])
            writer.writeheader()
            writer.writerows([{**row,"fictional":"true"} for row in rows])
    october=data["monthly_revenue"][-1]["actual_revenue"]
    for title,dataset in REPORTS.items():
        pdf=canvas.Canvas(str(root/"pdf"/f"{title}.pdf"),pagesize=A4,invariant=1)
        y=800
        lines=[title,"FICTIONAL - Nexora Solutions (Pvt) Ltd - Business services",
               "May to October 2026 | Approximately 150 employees | Monetary values: LKR",
               f"October revenue: {october:,} LKR. September revenue: 16,000,000 LKR.",
               "October decline: Atlas client acceptance moved to November, deferring billing.",
               "Risk: Operations capacity pressure; Atlas is 14 days late in October.",
               "Management action: review staffing and client acceptance milestones."]
        lines += [", ".join(f"{k}: {v}" for k,v in row.items()) for row in data[dataset]]
        if title=="Operations Report":
            lines += [str(row) for row in data["project_performance"]]
        import textwrap
        for line in lines:
            for part in textwrap.wrap(line,95):
                if y<50:
                    pdf.showPage();y=800
                pdf.setFont("Helvetica",9);pdf.drawString(35,y,part);y-=15
        pdf.save()
    return data

def read_dataset(path: Path, name: str):
    with path.open(encoding="utf-8",newline="") as stream:
        reader=csv.DictReader(stream)
        if set(reader.fieldnames or []) != {*SCHEMAS[name],"fictional"}:
            raise ValueError("Invalid dataset columns")
        rows=[]
        for source in reader:
            if source["fictional"] != "true":
                raise ValueError("Dataset must be fictional")
            row={k:kind(source[k]) for k,kind in SCHEMAS[name].items()}
            if row["month"] not in [f"2026-{m:02d}" for m in range(5,11)]:
                raise ValueError("Invalid reporting month")
            if any(value<0 for value in row.values() if isinstance(value,int)):
                raise ValueError("Negative business value")
            rows.append(row)
        keys=[tuple(r[k] for k in KEYS[name]) for r in rows]
        if len(keys)!=len(set(keys)):
            raise ValueError("Duplicate business key")
        if not rows:
            raise ValueError("Dataset is empty")
        if name=="employee_turnover" and any(r["opening_headcount"]+r["hires"]-r["departures"]!=r["closing_headcount"] for r in rows):
            raise ValueError("Headcount does not reconcile")
        if name=="project_performance" and any(r["actual_days"]-r["planned_days"]!=r["delay_days"] for r in rows):
            raise ValueError("Project delay does not reconcile")
        if name=="operational_kpis" and any(r["sla_percent"]>100 or r["target_percent"]>100 for r in rows):
            raise ValueError("Invalid percentage")
        return rows

