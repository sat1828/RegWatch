from __future__ import annotations

import json
from typing import Any

import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class VectorStoreService:
    def __init__(self) -> None:
        self._index: Any = None
        self._initialized = False
        self.dimension = settings.pinecone_dimension

    async def _ensure_index(self) -> Any:
        if self._initialized:
            return self._index

        api_key = settings.pinecone_api_key
        if api_key and api_key.get_secret_value():
            try:
                from pinecone import Pinecone

                pc = Pinecone(api_key=api_key.get_secret_value())
                if settings.pinecone_index_name not in pc.list_indexes().names():
                    logger.info("creating_pinecone_index", name=settings.pinecone_index_name)
                    pc.create_index(
                        name=settings.pinecone_index_name,
                        dimension=self.dimension,
                        metric="cosine",
                        spec={"serverless": {"cloud": "aws", "region": "us-east-1"}},
                    )
                self._index = pc.Index(settings.pinecone_index_name)
                self._initialized = True
            except Exception as e:
                logger.warning("pinecone_init_failed", error=str(e))

        return self._index

    async def upsert_vectors(
        self, vectors: list[dict[str, Any]], namespace: str = "default"
    ) -> bool:
        index = await self._ensure_index()
        if not index:
            logger.warning("pinecone_not_available_vector_upsert")
            return False

        try:
            index.upsert(vectors=vectors, namespace=namespace)
            return True
        except Exception as e:
            logger.error("vector_upsert_error", error=str(e))
            return False

    async def query_similar(
        self,
        query_vector: list[float],
        top_k: int = 5,
        namespace: str = "default",
        filter_dict: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        index = await self._ensure_index()
        if not index:
            return []

        try:
            result = index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True,
            )
            return [
                {
                    "id": m.id,
                    "score": m.score,
                    "metadata": m.metadata or {},
                }
                for m in result.matches
            ]
        except Exception as e:
            logger.error("vector_query_error", error=str(e))
            return []

    async def delete_vectors(
        self, ids: list[str], namespace: str = "default"
    ) -> bool:
        index = await self._ensure_index()
        if not index:
            return False
        try:
            index.delete(ids=ids, namespace=namespace)
            return True
        except Exception as e:
            logger.error("vector_delete_error", error=str(e))
            return False


vector_store = VectorStoreService()
