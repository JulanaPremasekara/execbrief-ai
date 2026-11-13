import hashlib
from langchain_postgres import PGVector
from langchain_core.documents import Document as LCDocument
from sqlalchemy import text
from execbrief.domain.entities.document import Document

class VectorStore:
    def __init__(self,engine,embeddings):
        self.engine=engine
        self.store=PGVector(embeddings=embeddings,connection=engine,collection_name="execbrief_phase2",
            embedding_length=384,use_jsonb=True,create_extension=False)

    def replace_source(self,source,documents):
        # Content-addressed IDs make retries idempotent. Remove stale chunks only after new chunks succeed.
        ids=[hashlib.sha256((source+str(i)+d.content).encode()).hexdigest() for i,d in enumerate(documents)]
        docs=[LCDocument(page_content=d.content,metadata={**d.metadata,"source_id":source}) for d in documents]
        with self.engine.connect() as lock:
            lock.execute(text("SELECT pg_advisory_lock(hashtext(:source))"),{"source":source})
            try:
                self.store.add_documents(docs,ids=ids)
                with self.engine.begin() as connection:
                    connection.execute(text("""DELETE FROM langchain_pg_embedding
                        WHERE collection_id=(SELECT uuid FROM langchain_pg_collection WHERE name='execbrief_phase2')
                        AND cmetadata->>'source_id'=:source AND NOT (id = ANY(:ids))"""),{"source":source,"ids":ids})
            finally:
                lock.execute(text("SELECT pg_advisory_unlock(hashtext(:source))"),{"source":source})
        return len(ids)

    def retrieve(self,query,k=5):
        if not query.strip() or not 1<=k<=50:
            raise ValueError("Provide a query and top-k between 1 and 50")
        documents=self.store.as_retriever(search_type="similarity",search_kwargs={"k":k}).invoke(query)
        return [Document(d.page_content,d.metadata) for d in documents]

