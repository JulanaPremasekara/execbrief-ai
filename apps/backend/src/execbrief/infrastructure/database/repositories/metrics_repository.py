from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from execbrief.infrastructure.database.models.metrics import TABLES
from execbrief.infrastructure.data.synthetic import read_dataset, KEYS

class MetricsRepository:
    def __init__(self, engine):
        self.engine=engine

    def import_directory(self, root):
        datasets={name:read_dataset(root/f"{name}.csv",name) for name in TABLES}
        for row in datasets["monthly_revenue"]:
            sales=[s for s in datasets["sales_performance"] if s["month"]==row["month"]]
            if sum(s["revenue"] for s in sales)!=row["actual_revenue"]:
                raise ValueError("Sales and revenue do not reconcile")
        with self.engine.begin() as connection:
            for name,rows in datasets.items():
                table=TABLES[name]
                for row in rows:
                    statement=insert(table).values(**row)
                    connection.execute(statement.on_conflict_do_update(index_elements=KEYS[name],
                        set_={key:statement.excluded[key] for key in row if key not in KEYS[name]}))
        return {name:len(rows) for name,rows in datasets.items()}

    def fetch(self, dataset):
        if dataset not in TABLES:
            raise ValueError("Unknown dataset")
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(select(TABLES[dataset])).mappings()]

