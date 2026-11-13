from langchain_community.document_loaders import PyPDFLoader
from execbrief.domain.entities.document import Document
class PDFLoader:
    def load(self,path):
        return [Document(d.page_content,{**d.metadata,"filename":path.name,"source":str(path),
            "document_id":"pdf/"+path.name,"page":int(d.metadata["page"])+1,"kind":"pdf"})
            for d in PyPDFLoader(str(path)).load()]

