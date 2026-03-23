from typing import List

def chunk_text(text: str, chunk_size: int = 150, overlap: int = 50) -> List[str]:
    """
    Extremely deterministic sliding window chunker operating on words.
    Avoids complex dependency footprints (like unstructured or heavy tiktoken).
    """
    if not text:
        return []
    
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        
        # Advance by size minus overlap, ensuring we move forward
        step = chunk_size - overlap
        if step <= 0:
            step = 1 # Fallback safeguard
        i += step
        
    return chunks
