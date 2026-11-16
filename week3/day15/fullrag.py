# ------------------------------------------------------------------------
# PART 1 - imports and environment setup
# ------------------------------------------------------------------------

import os
import json
from groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType

load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")
QDRANT_API_KEY=os.getenv("QDRANT_API_KEY")
QDRANT_URL=os.getenv("QDRANT_URL")



# ------------------------------------------------------------------------
# PART 2 - connecting to qdrant
# ------------------------------------------------------------------------

qclient=QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)
print("Connected to Qdrant Cloud!")



# ------------------------------------------------------------------------
# PART 3 - creating qdrant collection
# ------------------------------------------------------------------------

COLLECTION_NAME="knowledge_base"
EMBEDDING_SIZE=384

# Delete collection if it already exists
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

print(f"Collection created: {COLLECTION_NAME}")

# Creating payload index
qclient.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)


# ------------------------------------------------------------------------
# PART 4 - loading knowledge
# ------------------------------------------------------------------------

with open("knowledge.json", "r", encoding="utf-8") as file:
    documents=json.load(file)

# ------------------------------------------------------------------------
# PART 5 - create embedding
# ------------------------------------------------------------------------

print("Loading embedding model...")
emb_model=SentenceTransformer("all-MiniLM-L6-v2")

text=[document["text"] for document in documents]

embedding_doc=emb_model.encode(text)

print(f"Generated {len(embedding_doc)} embeddings")
print(f"Embedding size: {len(embedding_doc[0])}")


# ------------------------------------------------------------------------
# PART 6 - creating qdrant points
# ------------------------------------------------------------------------

points=[]

for i in range(len(documents)):
    point=PointStruct(
        id=i+1,
        vector=embedding_doc[i].tolist(),
        payload=documents[i]
    )
    points.append(point)



# ------------------------------------------------------------------------
# PART 7 - uploading to qdrant
# ------------------------------------------------------------------------

qclient.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"Uploaded {len(points)} documents to Qdrant!")



# ------------------------------------------------------------------------
# PART 8 - searching in qdrant
# ------------------------------------------------------------------------

def search(query):
    query_vector=emb_model.encode(query).tolist()

    result=qclient.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=1,
        with_payload=True
    ).points

    return result


def search_with_filter(query, query_filter=None):
    query_vector=emb_model.encode(query).tolist()

    result=qclient.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=1,
        with_payload=True,
        query_filter=query_filter
    ).points

    return result


filter=Filter(
    should=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        ),
        FieldCondition(
            key="category",
            match=MatchValue(value="leave")
        ),

    ]
)


# ------------------------------------------------------------------------
# test searching
# ------------------------------------------------------------------------

query = "How many vacation days do I get?"

# results = search_with_filter(query, filter)

# for result in results:
#     print(f"Score: {result.score:.3f}")
#     print(result.payload["text"])
#     print()


# ------------------------------------------------------------------------
# PART 9 - connecting to Groq and generating the answer
# ------------------------------------------------------------------------

grclient=Groq(api_key=GROQ_API_KEY)

def ask_llm(question, context):
    prompt = f"""
    Answer the question using only the information provided below.

    Context:
    {context}

    Question:
    {question}

    If the answer is not present in the context, say:
    "I don't know based on the provided information."
    """

    response = grclient.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content



question = "How many vacation days do I get?"
results = search_with_filter(question, filter)

# Extract text from the search results
context = "\n".join(
    result.payload["text"]
    for result in results
)


answer = ask_llm(question, context)


print("\nFinal Answer:")
print(answer)