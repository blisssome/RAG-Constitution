import os
from dotenv import load_dotenv

import pickle
import numpy as np
import faiss
import ollama

from typing import List

from dataclasses import asdict

from document_parser import DocumentChunk


load_dotenv()

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION"))

def embed(texts: List[str]) -> np.ndarray:
    embeddings = []

    for text in texts:
        result = ollama.embeddings(
            model=EMBEDDING_MODEL,
            prompt=text
        )
        embeddings.append(result["embedding"])

    return np.array(embeddings, dtype="float32")

class Database:
    
    def __init__(self):
        self.dimension = EMBEDDING_DIMENSION
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts = []
        self.metadata = []
    
    def add(self, chunks: List[DocumentChunk]):
        texts = [asdict(c)["text"] for c in chunks]
        metadata = [asdict(c)["metadata"] for c in chunks]

        embeddings = embed(texts)

        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {embeddings.shape[1]}")

        self.index.add(embeddings)
        self.texts.extend(texts)
        self.metadata.extend(metadata)

    def search(self, query: str, top_k: int = 5):
        query_embedding = embed([query])
        dist, indices = self.index.search(query_embedding, top_k)

        results = []

        for dist, i in zip(dist[0], indices[0]):
            if i != -1:
                results.append({
                    "text": self.texts[i],
                    "metadata": self.metadata[i],
                    "distance": float(dist)
                })

        return results

if __name__ == "__main__":
    from document_parser import parse_constitution, read_file
    text = read_file("./data/constitution_en-1-10.pdf")
    chunks = parse_constitution(text)
    db = Database()
    db.add(chunks)

    print(f"Added {len(chunks)} chunks to the database.")

    query = "Who holds legislative power according to the constitution of the Azerbaijan Republic?"

    results = db.search(query, top_k=5)

    for result in results:
        print("-" * 80)
        print(f"Distance: {result['distance']:.4f}")
        print(f"Metadata: {result['metadata']}")
        print(f"Text: {result['text']}")
        print("-" * 80)
