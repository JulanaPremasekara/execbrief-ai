import re
from execbrief.domain.entities.response_block import Block

class ResponsePlanner:
    def resolve(self,response,datasets,sources):
        blocks=[]
        for i,item in enumerate(response["blocks"]):
            id=f"b{i+1}"
            if item["type"]=="text":
                content=item["content"]
                citations=item.get("sources",[])
                if any(s not in sources for s in citations):
                    raise ValueError("Unknown source")
                if content.startswith("Recommendation:"):
                    if re.search(r"\d",content) or not citations:
                        raise ValueError("Recommendations need evidence and cannot invent numbers")
                elif not citations or not any(content==sources[s]["content"] for s in citations):
                    raise ValueError("Factual statements must match verified evidence")
                blocks.append(Block(id,"text",content))
            else:
                data=datasets.get(item["dataset_id"])
                if not data or not data["rows"] or item["chart_type"] not in ("bar","line"):
                    raise ValueError("Unapproved chart")
                if item["x"] not in data["columns"] or not item["y"] or not set(item["y"])<=set(data["columns"]):
                    raise ValueError("Unapproved chart columns")
                if any(v is not None and type(v) not in (int,float) for row in data["rows"] for v in [row[y] for y in item["y"]]):
                    raise ValueError("Non-numeric chart series")
                spec=dict(id=id,type="chart",chart_type=item["chart_type"],title=item["dataset_id"].replace("_"," ").title(),
                          dataset_id=item["dataset_id"],x=item["x"],y=item["y"])
                blocks.append(Block(id,"chart",spec=spec,dataset=data))
        return blocks

