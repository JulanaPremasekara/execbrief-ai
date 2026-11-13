from langchain_text_splitters import RecursiveCharacterTextSplitter
from execbrief.domain.entities.document import Document
class TextSplitter:
    def __init__(self):
        self.splitter=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200)
    def split(self,documents):
        result=[]
        for document in documents:
            parts=[document.content] if document.metadata["kind"]=="csv" else self.splitter.split_text(document.content)
            result.extend(Document(part,{**document.metadata,"chunk_index":i}) for i,part in enumerate(parts))
        return result

