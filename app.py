import os
import numpy as np
import pickle

import langchain
from langchain_huggingface import HuggingFaceEmbeddings

from transformers import pipeline
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import *
from vector_indexer import *
from swagger_config import *
from retriever import *


"""GLOBAL VARIABLES"""
user_context = {}
embeddings = None
generation_model = None


"""Model Utils"""
def load_retrieval_model():
    global embeddings
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        # embeddings = BGEM3FlagModel(EMBEDDING_MODEL_NAME, use_fp16=True)

def load_generation_model():
    global generation_model
    if generation_model is None:
        generation_model = pipeline(
            "text-generation",
            model=GENERATION_MODEL_NAME,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device_map="auto"
        )
        
load_retrieval_model()
load_generation_model()


def prepare_data():
    """Loads Document, Chunks, Indexes into Faiss"""
    index = load_faiss_index(INDEX_PATH)
    chunks = load_chunks(CHUNKS_PATH)
    docid_to_company_map = load_docid_map(DOC_ID_MAP_PATH)
    
    if index and chunks and docid_to_company_map:
        print("Loading chunks, doc-company mapping and index from existing files")
        return index, docid_to_company_map, chunks
    else:
        print("Creating index, chunks, docid map since existing file not present")
        documents = load_documents(DATA_PATH)
        chunks = chunk_documents(documents)
        index = create_faiss_index(chunks, embeddings, INDEX_PATH)
        docid_to_company_map = create_docid_company_mapping(chunks)
        save_chunks(chunks, CHUNKS_PATH)
        save_docid_map(docid_to_company_map, DOC_ID_MAP_PATH)

        return index, docid_to_company_map, chunks


# ------------------- Conversational Context Management --------------------------

def get_user_conversation(user_email):
    return user_context.get(user_email, "")

def update_user_conversation(user_email, query, response):
    if user_email not in user_context:
        user_context[user_email] = ""
    user_context[user_email] += f"User Query: {query}\nAssistant: {response}\n"

def reset_user_conversation(user_email):
    user_context[user_email] = ""

def inject_conversation_history(user_email, query):
    """Append user past conversational history to the current query."""
    context = get_user_conversation(user_email)
    if context:
        query_with_context = f"Previous conversation: {context}\n User Query: {query}"
    else:
        query_with_context = f"User Query: {query}"
    return query_with_context


# --------------------- Routes -------------------------- #

app = Flask(__name__)
CORS(app)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/static/swagger.json")
def swagger_json():
    return jsonify(SWAGGER_JSON)

# Chunk documents and index into VectoDB
index, docid_to_company_map, chunks = prepare_data()

@app.route("/chat", methods=["POST"])
def chat():    
    data = request.get_json()
    user_email = data.get("user_email")
    query = data.get("query")

    if not user_email or not query:
        return jsonify({"error": "Missing user_email or query"}), 400

    load_retrieval_model()
    load_generation_model()

    # inject previous conversation history
    query = inject_conversation_history(user_email, query)

    retrieved_chunks = retrieve_chunks(
        query, index, user_email, docid_to_company_map, chunks, embeddings
    )
    response = generate_response(query, retrieved_chunks, generation_model)
    print('\n----- Answer ------\n')
    print(response)

    update_user_conversation(user_email, query, response)
    return jsonify({"response": response})


@app.route("/reset_context", methods=["POST"])
def reset_context():
    data = request.get_json()
    user_email = data.get("user_email")

    if not user_email:
        return jsonify({"error": "Missing user_email"}), 400

    reset_user_conversation(user_email)
    return jsonify({"message": "Conversation context cleared."})


if __name__ == "__main__":
    print("Server Running")
    app.run(host="0.0.0.0", debug=False, port=5000)