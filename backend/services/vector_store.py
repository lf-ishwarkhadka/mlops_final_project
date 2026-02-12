import uuid
from dataclasses import dataclass

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from backend.config import QdrantConfig


@dataclass
class SearchResult:
    content: str
    source: str
    score: float


class VectorStoreService:
    """Manages vector storage and retrieval using self-hosted Qdrant."""

    def __init__(self, config: QdrantConfig):
        self._config = config
        self._client = None

    def connect(self) -> None:
        if self._config.use_local:
            self._client = QdrantClient(path=self._config.local_path)
        else:
            self._client = QdrantClient(
                host=self._config.host,
                port=self._config.port,
            )
        self._ensure_collection_exists()

    def store_embeddings(
        self,
        embeddings: list[list[float]],
        texts: list[str],
        source: str = None,
    ) -> int:
        """Store text embeddings in the vector database. Returns count stored."""
        self._ensure_connected()

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={"content": text, "source": source},
            )
            for embedding, text in zip(embeddings, texts)
        ]

        self._client.upsert(
            collection_name=self._config.collection_name,
            points=points,
        )

        return len(points)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[SearchResult]:
        """Find the most similar documents to the query embedding."""
        self._ensure_connected()

        result = self._client.query_points(
            collection_name=self._config.collection_name,
            query=query_embedding,  # ← important: it's 'query', not 'query_vector'
            limit=top_k,
            with_payload=True,
        )

        hits = result.points

        results = [
            SearchResult(
                content=hit.payload.get("content", ""),
                source=hit.payload.get("source", ""),
                score=hit.score,
            )
            for hit in hits
        ]

        return results

    def get_collection_count(self) -> int:
        """Return the number of vectors in the collection."""
        self._ensure_connected()
        info = self._client.get_collection(self._config.collection_name)
        return info.points_count

    def get_all_chunks(self, limit: int = 20, offset: int = 0) -> list[dict]:
        """Return stored chunks with their metadata."""
        self._ensure_connected()

        results, _next_offset = self._client.scroll(
            collection_name=self._config.collection_name,
            limit=limit,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        return [
            {
                "id": str(point.id),
                "content": point.payload.get("content", ""),
                "source": point.payload.get("source", ""),
            }
            for point in results
        ]

    def _ensure_collection_exists(self) -> None:
        collections = self._client.get_collections().collections
        existing_names = {c.name for c in collections}

        if self._config.collection_name not in existing_names:
            self._client.create_collection(
                collection_name=self._config.collection_name,
                vectors_config=VectorParams(
                    size=self._config.vector_size,
                    distance=Distance.COSINE,
                ),
            )
        
    def _ensure_connected(self) -> None:
        if self._client is None:
            raise RuntimeError("Not connected to Qdrant. Call connect() first.")
