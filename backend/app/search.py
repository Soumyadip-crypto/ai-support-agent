import chromadb
from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


client = chromadb.PersistentClient(
    path="./chroma_db"
)


collection = client.get_or_create_collection(
    name="support_knowledge"
)


questions = [
    "How long do I have to request a refund?"
]


for question in questions:

    query_embedding = model.encode(
        question
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )

    print("\nQuestion:", question)

    print(
        "Matched documents:",
        results["ids"][0]
    )

    print(
        "Distances:",
        results["distances"][0]
    )

    print(
        "Relevant text:",
        results["documents"][0][0]
    )