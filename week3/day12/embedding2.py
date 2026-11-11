from sentence_transformers import SentenceTransformer

# Load a pretrained embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

sentences = [
    "How can I reset my password?",
    "I forgot my login credentials.",
    "What is the capital of India?"
]

# Generate embeddings
embeddings = model.encode(sentences)

# Display results
for sentence, embedding in zip(sentences, embeddings):
    print("Sentence:", sentence)
    print("Vector dimensions:", len(embedding))
    print("Embedding:", embedding[:5])
    print("-" * 50)
