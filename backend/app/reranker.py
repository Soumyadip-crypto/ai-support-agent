import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="support_knowledge"
)


question = "How long do I have to request a refund?"


query_embedding = embedding_model.encode(
    question
).tolist()


results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)


documents = results["documents"][0]
ids = results["ids"][0]


pairs = [
    [question, document]
    for document in documents
]


scores = reranker.predict(pairs)


ranked_results = sorted(
    zip(scores, ids, documents),
    reverse=True
)


print("\nQuestion:", question)

print("\nReranked Results:")

for score, document_id, document in ranked_results:

    print("\nScore:", score)
    print("ID:", document_id)
    print("Document:", document)


best_score, best_id, best_document = ranked_results[0]


print("\n==============================")
print("BEST RESULT")
print("==============================")

print("ID:", best_id)
print("Score:", best_score)
print("Document:", best_document)