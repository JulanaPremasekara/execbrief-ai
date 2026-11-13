from langchain_community.document_loaders import CSVLoader as LangChainCSVLoader
from execbrief.domain.entities.document import Document
class CSVLoader:
    def load(self,path):
        return [Document(d.page_content,{**d.metadata,"filename":path.name,"source":str(path),
            "document_id":"csv/"+path.name,"row":int(d.metadata["row"])+1,"dataset_id":path.stem,"kind":"csv"})
            for d in LangChainCSVLoader(str(path),encoding="utf-8").load()]

