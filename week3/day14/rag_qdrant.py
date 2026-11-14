import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv
from groq import Groq

# PART 1 - loading env
# ----------------------------------------------------

load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
QDRANT_URL=os.getenv("QDRANT_URL")

# PART 2 - connecting to Qdrant
# ----------------------------------------------------

qclient=QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)
print("Connected to Qdrant Cloud.")


# PART 3 - creating qdrant collection
# ----------------------------------------------------

COLLECTION_NAME="knowledge_base"
EMBEDDING_SIZE=384

# delete collection if it is already exists
if qclient.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection: {COLLECTION_NAME}")
    qclient.delete_collection(COLLECTION_NAME)

# creating collection
qclient.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(
        size=EMBEDDING_SIZE,
        distance=Distance.COSINE
    )
)

print(f"Created collection: {COLLECTION_NAME}")
print(f"Vector size: {EMBEDDING_SIZE}")
print("Distance: COSINE")


# PART 4 - loading our knowledgebase

with open("knowledge_base.txt", "r", encoding="utf-8") as file:
    documents=[
        line.strip()
        for line in file
        if line.strip()
    ]
print(f"Loaded {len(documents)} documents.")


# PART 5 - creating embedding of the document

print("Loading embedding model...")
emb_model=SentenceTransformer("all-miniLM-L6-v2")       #384

document_embedding=emb_model.encode(documents)

print(f"Generated {len(document_embedding)} embeddings")
print(f"Embedding size: {len(document_embedding[0])}")


# PART 6 - creating qdrant points

points=[]

for i, vector in enumerate(document_embedding):
    point=PointStruct(
        id=i+1,
        vector=vector.tolist(),
        payload={
            "text": documents[i]
        }
    )
    points.append(point)


# PART 7 - uploading to qdrant

qclient.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)


# PART 8 - search in qdrant

def search(query, top_k=3):
    # embedding the query
    query_embd=emb_model.encode(query).tolist()

    # searching the query in qdrant
    results=qclient.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embd,
        limit=top_k,
        with_payload=True
    ).points

    return results


# PART 9 - test search
# query="how much I will get for my fitness?"
# results=search(query,3)
# print("\nSearch results:")

# for result in results:
#     print(f"Score: {result.score:.3f}")
#     print(result.payload["text"])
#     print()


# PART 10 - connecting to groq

gclient=Groq(api_key=GROQ_API_KEY)

# PART 11 - ask the LLM

def ask_llm(question, context):
    sys_prompt=f"""
    Answer the question using only the information provided below.

    Context:
    {context}

    If the answer is not present in the context, say:
    "I don't know based on the provided information."
    """
    messages=[
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response=gclient.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages
    )

    return response.choices[0].message.content


# PART 12 - complete RAG pipeline

question="how much I will get for my fitness?"
results=search(question, 3)

context="\n".join(
    result.payload["text"]
    for result in results
)

answer=ask_llm(question, context)


print("\nFinal Answer:")
print(answer)