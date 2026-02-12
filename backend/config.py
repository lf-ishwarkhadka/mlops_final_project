from pydantic_settings import BaseSettings
from pathlib import Path


class ModelConfig(BaseSettings):
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    llm_model_name: str = "Qwen/Qwen2-0.5B-Instruct"
    max_new_token: int = 512


class ChunkingConfig(BaseSettings):
    chunk_size: int = 500
    chunk_overlap: int = 50


class QdrantConfig(BaseSettings):
    host: str = "localhost"
    port: int = 6333
    collection_name: str = "documents"
    vector_size: int = 384
    use_local: bool = False
    local_path: str = "qdrant_data"


class AppConfig(BaseSettings):
    model: ModelConfig = ModelConfig()
    chunking: ChunkingConfig = ChunkingConfig()
    qdrant: QdrantConfig = QdrantConfig()
    upload_dir: Path = Path("data/uploads")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
