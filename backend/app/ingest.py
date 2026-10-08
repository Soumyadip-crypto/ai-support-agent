import os
import chromadb
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

try:
    chroma_client.delete_collection(
        name="support_knowledge"
    )
except Exception:
    pass

collection = chroma_client.get_or_create_collection(
    name="support_knowledge"
)

knowledge_folder = "knowledge"

for filename in os.listdir(knowledge_folder):

    if not filename.endswith(".txt"):
        continue

    file_path = os.path.join(
        knowledge_folder,
        filename
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:
        text = file.read().strip()

    policy_name = filename.replace(
        "_policy.txt",
        " Policy"
    ).title()

    chunks = [
        chunk.strip()
        for chunk in text.split("\n\n")
        if chunk.strip()
    ]

    full_policy_context = (
        f"{policy_name}\n\n{text}"
    )

    for index, chunk in enumerate(chunks):

        document_text = (
            f"{policy_name}\n\n"
            f"{chunk}"
        )

        embedding_text = (
            f"{policy_name}\n\n"
            f"{full_policy_context}\n\n"
            f"Relevant section:\n"
            f"{chunk}"
        )

        embedding = embedding_model.encode(
            embedding_text
        ).tolist()

        document_id = (
            filename.replace(".txt", "")
            + f"_chunk_{index}"
        )

        collection.upsert(
            ids=[document_id],
            documents=[document_text],
            embeddings=[embedding],
            metadatas=[
                {
                    "source": filename,
                    "policy": policy_name,
                    "chunk_index": index
                }
            ]
        )

        print(f"Stored: {document_id}")

print("\nAll chunks stored successfully!")