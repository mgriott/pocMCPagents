import faiss
import os
import pickle
from local_embedder import LocalEmbeddingFunction
from preprocess import read_logs
import numpy as np  # Agrega esta línea al inicio

INDEX_FILE = "faiss_index.bin"
DOCS_FILE = "doc_store.pkl"

embedder = LocalEmbeddingFunction()
dimension = 384  # all-MiniLM-L6-v2 returns 384-dimensional vectors
index = faiss.IndexFlatL2(dimension)
doc_store = []  # Guarda los textos originales

def build_vector_store():
    global index, doc_store
    logs = read_logs()
    if not logs:
        print("[WARN] No hay logs para indexar.")
        return

    docs = list(set(logs))
    vectors = embedder(docs) #vectoriza
    vectors_np = np.array(vectors).astype("float32")  #conversión necesaria

    index.add(vectors_np)
    doc_store = docs

    faiss.write_index(index, INDEX_FILE) #Guarda el índice
    with open(DOCS_FILE, "wb") as f:
        pickle.dump(doc_store, f)

    print(f"[INFO] Indexados {len(docs)} documentos.")

def retrieve_similar(query, top_k=5):
    if not os.path.exists(INDEX_FILE):
        print("[ERROR] El índice no está construido aún.")
        return []

    index = faiss.read_index(INDEX_FILE)
    with open(DOCS_FILE, "rb") as f:
        doc_store = pickle.load(f)

    vector = embedder([query])
    vector_np = np.array(vector).astype("float32")  # 👈 ESTA LÍNEA es clave

    D, I = index.search(vector_np, top_k)
    return [doc_store[i] for i in I[0] if i < len(doc_store)]


def is_index_built():
    return os.path.exists(INDEX_FILE) and os.path.exists(DOCS_FILE)
