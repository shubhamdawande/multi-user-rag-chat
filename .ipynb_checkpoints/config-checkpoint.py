DATA_PATH = "./data"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
INDEX_PATH = "./db/faiss_index.bin"
CHUNKS_PATH = "./db/chunks.pkl"
DOC_ID_MAP_PATH = "./db/doc_id_map.pkl"

GENERATION_MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"

USER_DOC_MAPPING = {
    "alice@gmail.com": ["apple"],
    "bob@gmail.com": ["tesla"],
    "charlie@gmail.com": []
}