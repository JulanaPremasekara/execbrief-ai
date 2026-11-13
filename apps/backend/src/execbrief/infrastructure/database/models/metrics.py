from sqlalchemy import MetaData, Table, Column, String, BigInteger, CheckConstraint
from execbrief.infrastructure.data.synthetic import SCHEMAS, KEYS
metadata=MetaData(schema="execbrief")
TABLES={}
for name,fields in SCHEMAS.items():
    columns=[Column(key, String(100) if kind is str else BigInteger,primary_key=key in KEYS[name],nullable=False) for key,kind in fields.items()]
    checks=[CheckConstraint(f"{key} >= 0",name=f"{name}_{key}_nonnegative") for key,kind in fields.items() if kind is int]
    TABLES[name]=Table(name,metadata,*columns,*checks)

