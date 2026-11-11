import os
import numpy as np
from sentence_transformers import SentenceTransformer

model=SentenceTransformer("all-MiniLM-L6-v2") # vector size - 384

def cosine_similarity(a, b):
    return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))

text="BMW is a car brand."

# embedding=model.encode(text)
# print(embedding.shape)
# print(embedding)

t1="I want to buy a cycle"
t2="I do not have money"

v1=model.encode(t1)
v2=model.encode(t2)

print(cosine_similarity(v1, v2))
