from langchain_huggingface import HuggingFaceEmbeddings
from execbrief.core.data_config import ROOT
def build_embeddings():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=str(ROOT/".cache"/"embeddings"),model_kwargs={"device":"cpu"},
        encode_kwargs={"normalize_embeddings":True})

