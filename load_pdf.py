import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import re

# ============================================================================
# CUSTOM CHUNKING FUNCTION — Sentence/paragraph aware with overlap
# ============================================================================

def chunk_text(full_text, chunk_size=800, overlap_size=80):
    """
    Split text into sentence-aware chunks with overlap.
    
    Args:
        full_text: raw text to chunk
        chunk_size: target chunk size in chars (not hard limit, won't split mid-sentence)
        overlap_size: chars of overlap between consecutive chunks
    
    Returns:
        list of (chunk_text, chunk_index) tuples
    """
    # Guard against PDF extraction quirks: collapse multiple whitespace
    full_text = re.sub(r'\n\s*\n', '\n\n', full_text)  # normalize paragraph breaks
    full_text = re.sub(r' +', ' ', full_text)  # collapse multiple spaces
    
    # Try splitting on paragraph boundaries first, fall back to sentences
    # Paragraph split: two+ newlines
    paragraphs = re.split(r'\n\s*\n', full_text)
    
    # If paragraphs are too large or few, split further on sentences
    sentences = []
    for para in paragraphs:
        # Split on sentence boundaries: . ! ? followed by space
        # Use lookahead/lookbehind to keep punctuation with the sentence
        para_sents = re.split(r'(?<=[.!?])\s+', para)
        sentences.extend(para_sents)
    
    # Greedily pack sentences into chunks without exceeding chunk_size mid-sentence
    chunks = []
    current_chunk = ""
    
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        
        # If adding this sentence would exceed chunk_size, finalize current chunk
        # (unless current_chunk is empty, which means one sentence > chunk_size)
        if current_chunk and len(current_chunk) + len(sent) + 1 > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        
        # Add sentence to current chunk
        if current_chunk:
            current_chunk += " " + sent
        else:
            current_chunk = sent
    
    # Finalize last chunk
    if current_chunk:
        chunks.append(current_chunk)
    
    # Apply overlap: prepend last ~overlap_size chars of previous chunk to next
    overlapped_chunks = []
    for i, chunk in enumerate(chunks):
        if i > 0 and overlap_size > 0:
            prev_chunk = chunks[i - 1]
            # Take last overlap_size chars of previous chunk as prefix
            overlap_prefix = prev_chunk[-overlap_size:] if len(prev_chunk) > overlap_size else prev_chunk
            overlapped_chunks.append(overlap_prefix + " " + chunk)
        else:
            overlapped_chunks.append(chunk)
    
    return overlapped_chunks


# ============================================================================
# MAIN: Load PDF, chunk, embed, store in Chroma with cosine distance
# ============================================================================

def main():
    pdf_path = "CBT_Book.pdf"  # Update this path
    
    # Load PDF
    from pypdf import PdfReader
    reader = PdfReader(pdf_path)
    full_text = "".join(page.extract_text() for page in reader.pages)
    
    # Chunk text with custom splitter
    chunks = chunk_text(full_text, chunk_size=800, overlap_size=80)
    print(f"Created {len(chunks)} chunks")
    
    # Initialize embedding model (normalize embeddings for consistency)
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    # Embed all chunks (with normalization)
    embeddings = embedding_model.encode(
        chunks,
        convert_to_tensor=True,
        normalize_embeddings=True  # NEW: ensure normalized vectors
    )
    
    # Initialize Chroma client and create collection with COSINE distance (not L2)
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # CRITICAL: Specify cosine distance space at collection creation
    # This MUST be deleted and recreated if the collection already exists with L2 space
    collection = client.get_or_create_collection(
        name="addiction_coach_docs",
        metadata={"hnsw:space": "cosine"}  # NEW: explicit cosine distance
    )
    
    # Store chunks in Chroma with metadata
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "source": str(pdf_path),
            "chunk": i
        }
        for i in range(len(chunks))
    ]
    
    collection.upsert(
        ids=ids,
        embeddings=embeddings.tolist(),
        documents=chunks,
        metadatas=metadatas
    )
    
    print(f"Stored {len(chunks)} chunks in Chroma (cosine distance space)")
    print(f"Collection metadata: {collection.metadata}")


if __name__ == "__main__":
    main()