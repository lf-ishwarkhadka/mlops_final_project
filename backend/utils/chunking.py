from backend.config import ChunkingConfig
from pydantic import BaseModel

config = ChunkingConfig()


class TextChunk(BaseModel):
    content: str
    index: int


def split_text_into_chunks(text: str):

    clean_text = normalize_whitespace(text)
    raw_chunks = create_overlapping_window(
        clean_text, config.chunk_size, config.chunk_overlap
    )

    chunks = [
        TextChunk(content=content, index=i)
        for i, content in enumerate(raw_chunks)
        if content.strip()
    ]
    return chunks


def normalize_whitespace(text: str):
    clean_text = " ".join(text.split())
    return clean_text


def create_overlapping_window(text: str, window_size: int, overlap: int):
    step = window_size - overlap
    chunks = []
    for start in range(0, len(text), step):
        chunk = text[start : start + window_size]
        chunks.append(chunk)

        if start + window_size >= len(text):
            break

    return chunks

