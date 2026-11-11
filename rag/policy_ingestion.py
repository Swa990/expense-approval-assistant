
import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


POLICY_DIR = "data"
VECTOR_DB_PATH = "knowledge_base/faiss_index"
EMBEDDING_MODEL = "./models/all-MiniLM-L6-v2"


def get_embedding_model():

    if not os.path.isdir(EMBEDDING_MODEL):
        raise FileNotFoundError(f"Embedding model not found: {EMBEDDING_MODEL}")

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )


def load_policy_documents():

    loader = DirectoryLoader(
        POLICY_DIR,
        glob="*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()

    if not documents:
        raise ValueError(f"No Markdown policy documents found in {POLICY_DIR}")

    for document in documents:
        document.metadata.update({
            "policy_id": "EXP-POL-001",
            "policy_version": "1.0",
            "document_type": "expense_policy"
        })

    return documents


def split_policy_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n## ", "\n### ", "\n\n", "\n", " ", ""]
    )

    return splitter.split_documents(documents)


def build_policy_knowledge_base():

    documents = load_policy_documents()
    chunks = split_policy_documents(documents)
    embeddings = get_embedding_model()

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
    vector_store.save_local(VECTOR_DB_PATH)

    return {
        "documents": len(documents),
        "chunks": len(chunks),
        "vector_store": VECTOR_DB_PATH
    }


if __name__ == "__main__":
    print(build_policy_knowledge_base())
