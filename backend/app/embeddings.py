import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="support_knowledge"
)


with open("knowledge/refund_policy.txt", "r", encoding="utf-8") as file:
    text = file.read()


embedding = model.encode(text).tolist()


collection.add(
    ids=["refund_policy"],
    documents=[text],
    embeddings=[embedding]
)


print("Refund policy stored successfully!")
def search_knowledge(query):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )

    return results["documents"][0][0]


question = "How long do I have to request a refund?"

result = search_knowledge(question)

print("\nQuestion:")
print(question)

print("\nRelevant Knowledge:")
print(result)