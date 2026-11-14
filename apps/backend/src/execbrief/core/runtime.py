import os
from execbrief.core import data_config

def execution_mode():
    mode=os.getenv("EXECBRIEF_MODE","mock")
    if mode not in ("live","mock"):
        raise ValueError("EXECBRIEF_MODE must be live or mock")
    return mode

