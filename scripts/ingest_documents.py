from execbrief.core.data_config import DATA_ROOT
from execbrief.core.container import build_ingestion
if __name__=="__main__":
    try:
        engine,store,use_case=build_ingestion()
        print("Ingested chunk counts:",use_case.execute(DATA_ROOT))
        print("Retrieved source filenames:",[d.metadata["filename"] for d in store.retrieve("Why did October revenue decline?")])
        engine.dispose()
    except Exception as error:
        print("Ingestion failed:",type(error).__name__,"Details suppressed; verify database and embedding model availability.")
        raise SystemExit(1)

