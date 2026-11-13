from pathlib import Path
from execbrief.domain.interfaces.document_ingestion import DocumentLoader, DocumentSplitter, DocumentStore
class IngestDocumentsUseCase:
    def __init__(self,loaders: dict[str,DocumentLoader],splitter:DocumentSplitter,store:DocumentStore):
        self.loaders,self.splitter,self.store=loaders,splitter,store
    def execute(self,root:Path):
        result={}
        for extension,loader in self.loaders.items():
            for path in sorted(root.rglob("*"+extension)):
                documents=self.splitter.split(loader.load(path))
                result[path.name]=self.store.replace_source(path.relative_to(root).as_posix(),documents)
        return result

