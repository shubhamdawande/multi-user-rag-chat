# Multi-User RAG Chat System

This repository contains a Python-based RAG (Retrieval-Augmented Generation) chat system that allows multiple users to query documents with restricted access, while maintaining conversational context. The system provides a REST API that can be accessed through a Swagger UI.

## Features

*   **Multi-User Support:** Handles concurrent queries from different users.
*   **Access Control:** Restricts user access to documents based on configured email mappings.
*   **Conversational Context:** Maintains a conversation history for each user, enabling follow-up questions.
*   **RAG Architecture:** Retrieves relevant document excerpts based on user queries, combined with a Large Language Model to produce accurate answers.
*   **REST API:** Provides a chat API using Flask, accessible via HTTP requests.
*   **Swagger UI:** Offers an interactive interface to explore the API endpoints.
*   **Persistent Indexing:** Saves index data and chunk information on disk for faster loading in subsequent runs.

# Multi-User RAG Chat System

This repository contains a Python-based RAG (Retrieval-Augmented Generation) chat system that allows multiple users to query documents with restricted access, while maintaining conversational context. The system provides a REST API that can be accessed through a Swagger UI.

## Features

*   **Multi-User Support:** Handles concurrent queries from different users.
*   **Access Control:** Restricts user access to documents based on configured email mappings.
*   **Conversational Context:** Maintains a conversation history for each user, enabling follow-up questions.
*   **RAG Architecture:** Retrieves relevant document excerpts based on user queries, combined with a Large Language Model to produce accurate answers.
*   **REST API:** Provides a chat API using Flask, accessible via HTTP requests.
*   **Swagger UI:** Offers an interactive interface to explore the API endpoints.
*   **Persistent Indexing:** Saves index data and chunk information on disk for faster loading in subsequent runs.

## How the System Works

This system operates using the Retrieval Augmented Generation (RAG) framework, enhanced with access control and conversational memory. Here's a breakdown of the core steps:

1.  **Document Chunking:**
    *   Input PDF documents are divided into smaller, manageable text chunks using a recursive character text splitter.
2.  **Vectorization:**
    *   Each text chunk is converted into a vector embedding using a Sentence Transformer based bi-encoder model.
3.  **Indexing:**
    *   The vector embeddings of all chunks are indexed using FAISS vectordb.
4.  **User Access Control:**
    *   User access is controlled by mapping user email addresses to the companies they have permission to access. Before a query is made, the system filters all indexes so that only the document chunks that the user has access to are considered.
5.  **Retrieval:**
    *   When a user submits a query, it is converted into a vector embedding using the same model. The system then searches the FAISS index using a combination of vector and BM25 search, retrieving the most relevant document chunks, filtered based on access control.
6.  **Answer Generation:**
    *   The retrieved document chunks and the user's query are passed to a Llama3.1 model. The LLM model uses the context from the retrieved document excerpts to generate a response to the user's query.
7. **Conversation Memory:**
     *   The user's question and the corresponding response is saved as part of conversation history. This conversational history is injected into next query sent by the user, which allows the LLM to give a contextual response.

## How to Run

1.  Ensure you have the required dependencies installed (specified in the requirements.txt).
2.  Place your PDF documents in the `./data` directory.
3.  Run the following command to start the server:
    ```bash
    python app.py
    ```
4.  Open your web browser and go to `http://127.0.0.1:5000/swagger` to access the Swagger UI and interact with the API.

## API Usage

The system exposes the following API endpoints:

### `/chat` (POST)
Send a query and get the generated response.

*   **Request Body (JSON):**
    ```json
    {
      "query": "Your question goes here",
      "user_email": "user@example.com"
    }
    ```
*   **Response (JSON):**
    ```json
    {
      "response": "The generated answer from the system."
    }
    ```
    *   `query` *(string)*: User's question.
    *  `user_email` *(string)*: Email address for access control and conversational memory.

### `/reset_context` (POST)
Clear the conversational context of a user

*   **Request Body (JSON):**
    ```json
    {
      "user_email": "user@example.com"
    }
    ```
*   **Response (JSON):**
   ```json
    {
      "message": "Conversation context cleared."
    }
   ```

## Example Users and Access
For sample testing, the system is configured with the following users and access mappings:

alice@gmail.com: Has access to documents related to the "Apple" company.

bob@gmail.com: Has access to documents related to the "Tesla" company.

charlie@gmail.com: Does not have access to documents of any specific company by default.

Note: These user mappings are defined in the USER_DOC_MAPPING within config.py.

USER_DOC_MAPPING:
```json
"alice@gmail.com": ["apple"],
"bob@gmail.com": ["tesla"],
"charlie@gmail.com": []
```

## Example Inputs and Outputs

Here are some examples to illustrate access control and conversational memory:

User = Alice

```json
QUERY 1:
{
  "query": "What is the revenue for apple in 2024?",
  "user_email": "alice@gmail.com"
  "generated_response": "According to the provided document excerpt, the total net sales for Apple Inc. in 2024 is $391,035 million."
}

QUERY 2:
{
  "query": "How are the sales numbers for iphones different for Asia vs Japan?",
  "user_email": "alice@gmail.com"
  "generated_response": "Based on the provided document excerpts, we can infer the following information about iPhone sales in Asia and Japan:\n\n* In Greater China, iPhone revenue represented a moderately higher proportion of net sales in 2024 compared to 2023.\n* In Japan, iPhone revenue was the primary driver of the increase in net sales during 2024, with a  higher net sales of iPhone compared to 2023.\n\nThere is no direct comparison between the sales numbers for iPhones in Asia and Japan, as the excerpts do not provide specific sales figures for these regions. However, we can infer that iPhone sales were strong in both regions, with Japan seeing an increase in net sales due to higher iPhone sales, and Greater China seeing a decrease in net sales due to lower iPhone sales.\n\nTo answer your question, the sales number for iPhones is higher in Japan compared to Greater China in 2024, as evidenced by the increase in net sales in Japan due to higher iPhone sales, and the decrease in net sales in Greater"
}

```

User = Bob

```json
QUERY 2:
{
  "query": "How are the sales numbers for iphones different for Asia vs Japan?",
  "user_email": "bob@gmail.com"
  "generated_response": "I don't have any information about iPhone sales in the provided document excerpts. The document appears to be a financial report from Tesla, Inc., and it does not mention iPhone sales at all. It seems to be focused on Tesla's products and services, including their automotive sales and revenue recognition. Therefore, I am unable to provide an answer to your question based on the provided information."
}

```

Please ensure that you have downloaded the required PDF files and have them saved in the ./data folder before using this application.

Use the USER_DOC_MAPPING constant within config.py to configure real user email addresses and their document access permissions.
