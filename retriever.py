import faiss
import numpy as np
from langchain_community.retrievers import BM25Retriever

from config import *

def filter_by_access(user_email, chunks, docid_to_company_map):
    """Filter the faiss results based on user access"""
    user_companies = USER_DOC_MAPPING.get(user_email, [])
    filtered_docids = []
    for docid, company in docid_to_company_map.items():
        if company in user_companies:
            filtered_docids.append(docid)

    filtered_chunks = [chunks[i] for i in filtered_docids]

    return filtered_chunks, filtered_docids

# Vector Retrieval and Answer Generation

def retrieve_chunks(query, index, user_email, docid_to_company_map, chunks, embeddings):
    """Retrieve relevant document chunks based on query and user access."""
    #filter based on user access
    filtered_chunks, filtered_docids = filter_by_access(user_email, chunks, docid_to_company_map)

    #vector search
    vector_embeddings = embeddings.embed_documents([chunk.page_content for chunk in filtered_chunks])
    query_embedding = embeddings.embed_query(query)
    dimension = len(vector_embeddings[0])

    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(np.array(vector_embeddings).astype("float32"))
    D, I = faiss_index.search(np.array([query_embedding]).astype("float32"), k=3)
    retrieved_chunks = [filtered_chunks[i] for i in I[0]]

    #BM25 search
    bm25 = BM25Retriever.from_documents(filtered_chunks)
    bm25.k = 3
    bm25_chunks = bm25.get_relevant_documents(query)
    retrieved_chunks.extend(bm25_chunks)

    return retrieved_chunks


def generate_response(query, retrieved_chunks, generation_model):
    """Generate response from LLM based on retrieved context."""
    context = "\n".join([chunk.page_content for chunk in retrieved_chunks])
    prompt = f"""
    ### Instruction: Use the following document excerpts from financial report to answer the question at the end.
    If answer is not found in the excerpts, try to answer with help of knowledge from your training data. Do not make up an answer, if you don't know.
    ---
    ### Context: {context}
    ---
    ### {query}
    """

    print('\n----- Prompt ------\n')
    print(prompt)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]    
    outputs = generation_model(
        messages,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7
    )

    response = outputs[-1]["generated_text"]
    if response[-1]['role'] != 'assistant':
        raise ValueError('No response found!!!')        
    return response[-1]['content']