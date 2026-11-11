
import os

from langchain_community.vectorstores import FAISS
from rag.policy_ingestion import get_embedding_model, VECTOR_DB_PATH


def load_policy_knowledge_base():

    index_path = os.path.join(VECTOR_DB_PATH, "index.faiss")

    if not os.path.exists(index_path):
        raise FileNotFoundError("Policy knowledge base not found. Build it first.")

    return FAISS.load_local(
        VECTOR_DB_PATH,
        get_embedding_model(),
        allow_dangerous_deserialization=True
    )


def retrieve_policy(query, k=5):

    vector_store = load_policy_knowledge_base()

    results = vector_store.similarity_search_with_score(
        query=query,
        k=k
    )

    return [
        {
            "policy_content": document.page_content,
            "metadata": document.metadata,
            "similarity_distance": float(distance)
        }
        for document, distance in results
    ]


if __name__ == "__main__":

    query = input("Enter policy search query: ").strip()

    if not query:
        raise ValueError("Search query cannot be empty.")

    results = retrieve_policy(query, k=5)

    for index, result in enumerate(results, 1):
        print(f"\n--- Retrieved Policy {index} ---")
        print("Content:", result["policy_content"])
        print("Metadata:", result["metadata"])
        print("Distance:", result["similarity_distance"])
