from execbrief.infrastructure.data.synthetic import generate, facts, read_dataset, SCHEMAS
from execbrief.infrastructure.rag.loaders.pdf_loader import PDFLoader
from execbrief.infrastructure.rag.loaders.csv_loader import CSVLoader
from execbrief.infrastructure.rag.text_splitter import TextSplitter
from execbrief.domain.entities.document import Document
from execbrief.application.use_cases.ingest_documents import IngestDocumentsUseCase

def test_consistent_generation(tmp_path):
    data=generate(tmp_path)
    assert data==facts()
    assert len(list((tmp_path/"pdf").glob("*.pdf")))==6
    for name in SCHEMAS:
        assert read_dataset(tmp_path/"csv"/f"{name}.csv",name)==data[name]
    for month in data["monthly_revenue"]:
        assert sum(r["revenue"] for r in data["sales_performance"] if r["month"]==month["month"])==month["actual_revenue"]
    for path in (tmp_path/"pdf").glob("*.pdf"):
        documents=PDFLoader().load(path)
        assert "14,000,000" in documents[0].content
        assert documents[0].metadata["page"]==1
        assert documents[0].metadata["filename"]==path.name
    before={p.name:p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    generate(tmp_path)
    assert before=={p.name:p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}

def test_invalid_import_rejected(tmp_path):
    import pytest
    generate(tmp_path)
    path=tmp_path/"csv"/"monthly_revenue.csv"
    path.write_text(path.read_text().replace("14000000","-1"),encoding="utf-8")
    with pytest.raises(ValueError,match="Negative"):
        read_dataset(path,"monthly_revenue")

def test_load_split_metadata(tmp_path):
    generate(tmp_path)
    documents=CSVLoader().load(tmp_path/"csv"/"monthly_revenue.csv")
    assert len(documents)==6
    assert documents[0].metadata["row"]==1
    assert documents[0].metadata["dataset_id"]=="monthly_revenue"
    assert TextSplitter().split(documents)[0].content==documents[0].content
    chunks=TextSplitter().split([Document("Repeated business evidence. "*200,{"kind":"pdf","page":2})])
    assert len(chunks)>1
    assert all(len(d.content)<=1000 and d.metadata["page"]==2 for d in chunks)

def test_ingestion_is_repeatable(tmp_path):
    generate(tmp_path)
    class Store:
        def __init__(self): self.sources={}
        def replace_source(self,source,documents):
            self.sources[source]=documents
            return len(documents)
    store=Store()
    use_case=IngestDocumentsUseCase({".pdf":PDFLoader(),".csv":CSVLoader()},TextSplitter(),store)
    first=use_case.execute(tmp_path)
    assert first==use_case.execute(tmp_path)
    assert len(store.sources)==12

def test_retriever_contract():
    from execbrief.infrastructure.rag.pgvector_store import VectorStore
    class Retriever:
        def invoke(self,query):
            from langchain_core.documents import Document
            return [Document(page_content="October evidence",metadata={"filename":"report.pdf"})]
    class Store:
        def as_retriever(self,**kwargs):
            assert kwargs=={"search_type":"similarity","search_kwargs":{"k":5}}
            return Retriever()
    adapter=object.__new__(VectorStore)
    adapter.store=Store()
    assert adapter.retrieve("October")[0].metadata["filename"]=="report.pdf"
