import numpy as np
import os
from backend.utils.chunk_and_index import load_faiss_index
from backend.utils.legal_embeddings import embed_text

def retrieve_top_k_chunks(query: str, k: int = 5, doc_hash=None, index=None, metadata=None):
    """
    Retrieve chunks. 
    'doc_hash' can now be:
      - A single string (one document)
      - A LIST of strings (multiple documents)
    """
    
    # CASE 1: SEARCH MULTIPLE DOCUMENTS
    if isinstance(doc_hash, list):
        aggregated_results = []
        
        # Search each document individually
        for single_hash in doc_hash:
            # Recursive call for single document
            results = retrieve_top_k_chunks(query, k=k, doc_hash=single_hash)
            aggregated_results.extend(results)
            
        # If we have too many, we rely on the LLM to filter, 
        # or we could re-rank here. For now, we take unique chunks.
        # (Simple de-duplication)
        unique_results = list(set(aggregated_results))
        return unique_results[:k*2] # Return slightly more for multi-doc context

    # CASE 2: SEARCH SINGLE DOCUMENT (Original Logic)
    # Load index if not provided
    if index is None or metadata is None:
        if doc_hash is None:
            return [] # No context provided
        
        index, metadata = load_faiss_index(doc_hash)
        
        if index is None or metadata is None:
            return []

    # Embed query
    query_vec = embed_text(query).reshape(1, -1).astype(np.float32)

    # Search FAISS
    # We ask for 'k' results from this specific doc
    D, I = index.search(query_vec, k)
    
    results = []
    for i in I[0]:
        if i < len(metadata):
            results.append(metadata[i]["text"])

    return results