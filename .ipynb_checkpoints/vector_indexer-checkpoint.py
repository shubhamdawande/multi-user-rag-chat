import faiss
from typing import List
import os
import numpy as np
import pickle

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from config import *

def load_documents(data_path: str) -> List:
    """Load PDF documents from a directory."""
    documents = []
    for filename in os.listdir(data_path):        
        if filename.endswith(".pdf"):
            print(f'Processing file: {filename}')
            loader = PyPDFLoader(os.path.join(data_path, filename))
            try:
                doc = loader.load()
            except:
                print(f'Skipping file: {filename}')
                continue
                
            for d in doc:
                d.metadata['filename'] = filename
            documents.extend(doc)
    return documents

def chunk_documents(documents: List) -> List:
    """Split documents into chunks with metadata."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = text_splitter.split_documents(documents)
    return chunks

def create_faiss_index(chunks: List, embeddings, index_path:str) -> faiss.Index:
        """Create and save a FAISS index from chunk embeddings."""
        vector_embeddings = embeddings.embed_documents([chunk.page_content for chunk in chunks])
        dimension = len(vector_embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(vector_embeddings).astype("float32"))
        faiss.write_index(index, index_path)
        print("FAISS index created and saved")
        return index

def load_faiss_index(index_path: str) -> faiss.Index:
    """Load a FAISS index from a file."""
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        print("FAISS index loaded from file.")
        return index
    else:
        print("FAISS index file not found.")
        return None

def save_chunks(chunks: List, path: str):
    """Save chunked documents to a pickle file."""
    with open(path, "wb") as f:
        pickle.dump(chunks, f)
    print("Chunks saved to disk")


def load_chunks(path: str) -> List:
    """Load chunked documents from a pickle file."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            chunks = pickle.load(f)
            print("Chunks loaded from disk.")
            return chunks
    else:
        print("Chunks file not found")
        return None

def create_docid_company_mapping(chunks):
    """Create mapping between doc id and company name from metadata"""
    doc_id_to_company_map = {}
    for i, chunk in enumerate(chunks):
        filename = chunk.metadata['filename']
        try:
            company_name, _ = os.path.splitext(filename)
        except:
            company_name = 'Unknown Company'
        doc_id_to_company_map[i] = company_name
    return doc_id_to_company_map

def save_docid_map(docid_to_company_map, path: str):
    """Save doc_id_to_company_map to a pickle file."""
    with open(path, "wb") as f:
        pickle.dump(docid_to_company_map, f)
    print("doc id map saved to disk")

def load_docid_map(path: str) -> dict:
    """Load doc_id_to_company_map from a pickle file."""
    if os.path.exists(path):
        with open(path, "rb") as f:
            docid_to_company_map = pickle.load(f)
            print("doc id map loaded from disk.")
            return docid_to_company_map
    else:
        print("doc id map file not found")
        return None