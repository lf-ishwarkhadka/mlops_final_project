import logging
import shutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from backend.config import AppConfig
from backend.services.embedding import EmbeddingService
from backend.services.llm import LLMService
from backend.services.rag import RAGOrchestrator
from backend.services.vector_store import VectorStoreService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


config = AppConfig()
embedding_service = EmbeddingService(config.model)
vector_store = VectorStoreService(config.qdrant)
llm_service = LLMService(config.model)
rag = RAGOrchestrator(config, embedding_service, vector_store, llm_service)




@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — loading models and connecting to Qdrant...")
    embedding_service.load()
    vector_store.connect()
    llm_service.load()
    logger.info("All services ready")
    yield
    logger.info("Shutting down")



app = FastAPI(
    title="RAG Microservice",
    description="Retrieval-Augmented Generation API with self-hosted models",
    version="1.0.0",
    lifespan=lifespan,
)




class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question")
    top_k: int = Field(
        default=5, ge=1, le=20, description="Number of chunks to retrieve"
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


class IndexResponse(BaseModel):
    filename: str
    chunks_stored: int
    message: str


class HealthResponse(BaseModel):
    status: str
    documents_count: int




@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the service is running and return collection stats."""
    try:
        count = vector_store.get_collection_count()
    except Exception:
        count = 0
    return HealthResponse(status="healthy", documents_count=count)


@app.post("/index", response_model=IndexResponse)
async def index_document(file: UploadFile = File(...)):
    """Upload a PDF or TXT file, chunk it, embed it, and store in Qdrant."""
    _validate_file(file)

    saved_path = _save_uploaded_file(file)
    try:
        result = rag.index_document(saved_path, file.filename)
        return IndexResponse(
            filename=result.filename,
            chunks_stored=result.chunks_stored,
            message=result.message,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Error indexing document")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {e}")
    finally:
        saved_path.unlink(missing_ok=True)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Ask a question and get an answer based on indexed documents."""
    try:
        result = rag.chat(question=request.question, top_k=request.top_k)
        return ChatResponse(answer=result.answer, sources=result.sources)
    except Exception as e:
        logger.exception("Error during chat")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")


@app.get("/chunks")
async def get_chunks(limit: int = 20, offset: int = 0):
    """View stored chunks in the vector database."""
    try:
        total = vector_store.get_collection_count()
        chunks = vector_store.get_all_chunks(limit=limit, offset=offset)
        return {
            "total_chunks": total,
            "showing": len(chunks),
            "offset": offset,
            "chunks": chunks,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




def _validate_file(file: UploadFile) -> None:
    allowed_types = {
        "application/pdf",
        "text/plain",
    }
    allowed_extensions = {".pdf", ".txt"}

    extension = Path(file.filename).suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: '{extension}'. Allowed: {allowed_extensions}",
        )


def _save_uploaded_file(file: UploadFile) -> Path:
    save_path = config.upload_dir / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return save_path
