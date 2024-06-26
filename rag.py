import os
import streamlit as st
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.duckdb import DuckDBVectorStore
from llama_index.core import StorageContext

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


@st.cache_resource
def init_model():
    """
    Initializes the model by setting up the Ollama language model and the Ollama embedding model.
    The function caches the result using the Streamlit cache_resource decorator.

    Returns:
        int: The dimension of the embeddings generated by the Ollama embedding model.
    """
    Settings.llm = Ollama(model="wizardlm2:7b-q5_K_M", request_timeout=300.0)

    Settings.embed_model = OllamaEmbedding(
        model_name="snowflake-arctic-embed:latest")
    embed_dim = len(Settings.embed_model.get_query_embedding('hello'))
    return embed_dim





@st.cache_resource
def init_index(rebuild=False):
    """
    Initializes a vector store index for a document retrieval system.

    This function sets up a DuckDBVectorStore and creates a VectorStoreIndex from a set of documents. If the `rebuild` parameter is True, it will remove any existing database files and recreate the index from scratch. Otherwise, it will load the index from the existing vector store.

    Args:
        rebuild (bool): If True, the index will be rebuilt from the documents. If False, the index will be loaded from the existing vector store.

    Returns:
        VectorStoreIndex: The initialized vector store index.
    """
    embed_dim = init_model()
    if rebuild:
        documents = SimpleDirectoryReader("./data").load_data()
        os.remove('duckdb/rag.db')
        os.removedirs('duckdb')

        vector_store = DuckDBVectorStore(
            embed_dim=embed_dim, database_name="rag.db", persist_dir="duckdb")

        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context)
    else:
        vector_store = DuckDBVectorStore(
            embed_dim=embed_dim, database_name="rag.db", persist_dir="duckdb")
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    return index





@st.cache_resource
def init_engine():
    """
    Initializes the chat engine for the application.

    Returns:
        chat_engine (ChatEngine): The initialized chat engine.
    """    
    index = init_index(rebuild=True)
    chat_engine = index.as_chat_engine(
        chat_mode="condense_question", verbose=True)
    return chat_engine
