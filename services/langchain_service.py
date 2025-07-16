import os
from langchain.embeddings.base import Embeddings
from langchain_mongodb import MongoDBAtlasVectorSearch, MongoDBChatMessageHistory

from config import Config


class LangchainService:
    """Helper for LangChain integrations using MongoDB."""

    def __init__(self, mongo_uri: str | None = None, db_name: str | None = None) -> None:
        self.mongo_uri = mongo_uri or Config.MONGODB_URI or "mongodb://localhost:27017/furdb"
        self.db_name = db_name or os.getenv("MONGO_DB", "furdb")

    def get_history(self, session_id: str) -> MongoDBChatMessageHistory:
        """Return a chat history object for the session."""
        return MongoDBChatMessageHistory(
            connection_string=self.mongo_uri,
            session_id=session_id,
            database_name=self.db_name,
            collection_name="chat_history",
        )

    def get_vector_store(
        self, embedding: Embeddings, namespace: str = "embeddings"
    ) -> MongoDBAtlasVectorSearch:
        """Return a vector store backed by MongoDB Atlas Vector Search."""
        ns = f"{self.db_name}.{namespace}"
        return MongoDBAtlasVectorSearch.from_connection_string(
            self.mongo_uri,
            ns,
            embedding,
        )


__all__ = ["LangchainService"]
