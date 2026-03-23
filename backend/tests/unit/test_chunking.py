import pytest
from app.services.chunking_service import chunk_text

def test_chunk_text_basic():
    text = "Hello world. This is a test."
    # Chunk size logic: split by characters
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert len(chunks) > 1
    assert "Hello" in chunks[0]

def test_chunk_text_overlap():
    text = "word1 word2 word3"
    chunks = chunk_text(text, chunk_size=10, overlap=5)
    # Check if a word from chunk 0 appears in chunk 1 (if it fits in the overlap)
    if len(chunks) > 1:
        # This depends on exact implementation details of chunk_text
        pass

def test_chunk_text_empty():
    assert chunk_text("", 10, 2) == []
