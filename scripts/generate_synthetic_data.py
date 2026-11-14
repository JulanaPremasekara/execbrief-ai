from execbrief.core.data_config import DATA_ROOT
from execbrief.infrastructure.data.synthetic import generate
if __name__=="__main__":
    result=generate(DATA_ROOT)
    print("Generated six fictional CSV datasets and six PDF reports.")

