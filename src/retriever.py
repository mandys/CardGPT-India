"""
Document Retrieval Service
Handles vector search, document storage, and similarity calculations
"""

import numpy as np
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# --- NEW ADVANCED SEMANTIC CHUNKING LOGIC ---

def _format_key_to_natural_language(key: str) -> str:
    """Converts a snake_case key to a readable title."""
    return key.replace('_', ' ').title()


def _traverse_and_chunk(node: Any, card_name: str, source_file: str, path: str) -> List[Dict]:
    """
    (Corrected Version)
    Recursively traverses a JSON node, creating small, semantic chunks.
    This version ensures that nested dictionaries are fully included in their parent's chunk.
    """
    chunks = []

    if isinstance(node, dict):
        # This dictionary will become a single chunk.
        content_parts = []
        
        # First, process all children of this node to create readable content.
        for key, value in node.items():
            # If the child is another dictionary, format it neatly.
            if isinstance(value, dict):
                # Create a readable sub-section for the nested dictionary.
                sub_parts = [f"  - {_format_key_to_natural_language(k)}: {v}" for k, v in value.items()]
                readable_value = f"\n{_format_key_to_natural_language(key)}:\n" + "\n".join(sub_parts)
                content_parts.append(readable_value)
            # If the child is a list, format it.
            elif isinstance(value, list):
                 # We can handle list formatting here if needed, for now just join them
                readable_value = ", ".join(map(str, value))
                content_parts.append(f"- {_format_key_to_natural_language(key)}: {readable_value}")
            # Otherwise, it's a simple key-value pair.
            else:
                content_parts.append(f"- {_format_key_to_natural_language(key)}: {value}")
        
        # Assemble the full content for the current dictionary chunk.
        parent_key_formatted = _format_key_to_natural_language(path.split('.')[-1]) if path else "Card Info"
        content = f"{parent_key_formatted}:\n" + "\n".join(content_parts)
        
        chunks.append({
            "id": f"{card_name}_{path.replace('.', '_')}",
            "cardName": card_name,
            "content": content,
            "section": path,
            "metadata": {
                "section": path,
                "cardType": card_name,
                "source_file": source_file,
                "chunk_type": "semantic_grouped"
            }
        })
        
        # NOW, we recurse into any complex children to create MORE GRANULAR chunks.
        # This gives us both the complete parent view and the detailed child view.
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                new_path = f"{path}.{key}" if path else key
                chunks.extend(_traverse_and_chunk(value, card_name, source_file, new_path))

    elif isinstance(node, list):
        for i, item in enumerate(node):
            new_path = f"{path}[{i}]"
            chunks.extend(_traverse_and_chunk(item, card_name, source_file, new_path))
            
    return chunks


class DocumentRetriever:
    """Service for storing documents and performing vector similarity search"""
    
    def __init__(self):
        """Initialize the document retriever"""
        self.documents: List[Dict] = []
        self.embeddings: List[Optional[List[float]]] = []
        self.is_indexed = False
    
    def load_documents_from_json(self, data_directory: str = "data") -> List[Dict]:
        """
        Load and process credit card documents from JSON files using advanced
        semantic chunking strategy.
        
        Args:
            data_directory: Directory containing JSON files
            
        Returns:
            A list of small, granular documents (chunks).
        """
        data_path = Path(data_directory)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path.absolute()}")
        
        json_files = list(data_path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {data_path}")
        
        all_chunks = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    card_data = json.load(f)
                    card_name = self._extract_card_name(json_file.name)
                    
                    # Process common_terms with new chunking
                    if 'common_terms' in card_data:
                        common_chunks = _traverse_and_chunk(
                            card_data['common_terms'], 
                            card_name, 
                            json_file.name, 
                            'common_terms'
                        )
                        all_chunks.extend(common_chunks)
                    
                    # Process card-specific data with new chunking
                    if 'card' in card_data:
                        card_chunks = _traverse_and_chunk(
                            card_data['card'], 
                            card_name, 
                            json_file.name, 
                            'card'
                        )
                        all_chunks.extend(card_chunks)

            except Exception as e:
                logger.error(f"Error loading and chunking {json_file}: {str(e)}")
                continue
        
        logger.info(f"Loaded and chunked {len(json_files)} files into {len(all_chunks)} semantic chunks.")
        self.documents = all_chunks
        return all_chunks
    
    def store_documents_and_embeddings(self, documents: List[Dict], embeddings: List[List[float]]):
        """Store documents and their corresponding embeddings"""
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        self.documents = documents
        self.embeddings = [np.array(e) for e in embeddings if e is not None]  # Store as numpy arrays
        self.is_indexed = True
        
        logger.info(f"Stored {len(documents)} documents with embeddings")
    
    def search_similar_documents(
        self, 
        query_embedding: List[float], 
        top_k: int = 5,
        threshold: float = 0.0,
        card_filter: Optional[str] = None,
        boost_keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for documents similar to the query embedding with efficient pre-filtering.
        
        Args:
            query_embedding: Vector representation of the query
            top_k: Number of top results to return
            threshold: Minimum similarity threshold
            card_filter: Filter by specific card name
            boost_keywords: Keywords to boost in search
            
        Returns:
            List of similar documents with similarity scores
        """
        if not self.is_indexed:
            raise ValueError("Documents not indexed. Call store_documents_and_embeddings first.")
        
        query_embedding_np = np.array(query_embedding)
        
        # 1. EFFICIENT PRE-FILTERING (The core improvement)
        # This step drastically reduces the search space.
        candidate_indices = []
        if card_filter:
            # We only consider documents that match the card name.
            for i, doc in enumerate(self.documents):
                if doc.get('cardName', '').lower() == card_filter.lower():
                    candidate_indices.append(i)
            logger.info(f"Filtering search to {len(candidate_indices)} chunks for card: {card_filter}")
        else:
            # If no filter, we search through all documents.
            candidate_indices = list(range(len(self.documents)))
        
        # 2. SIMILARITY CALCULATION (on the smaller, filtered set)
        similarities = []
        for idx in candidate_indices:
            doc = self.documents[idx]
            doc_embedding = self.embeddings[idx]
            
            if doc_embedding is None:
                continue
            
            similarity = self._cosine_similarity(query_embedding_np, doc_embedding)
            
            # Apply keyword boosting if specified
            if boost_keywords:
                similarity = self._apply_keyword_boost(doc, similarity, boost_keywords)
            
            if similarity >= threshold:
                similarities.append((similarity, idx))
        
        # 3. RANKING
        similarities.sort(key=lambda x: x[0], reverse=True)
        top_results = similarities[:top_k]
        
        # Build result documents
        results = []
        for similarity, idx in top_results:
            doc = self.documents[idx].copy()
            doc["similarity"] = similarity
            results.append(doc)
        
        logger.info(f"Found {len(results)} similar documents from {len(candidate_indices)} candidates.")
        return results
    
    def get_available_cards(self) -> List[str]:
        """Get list of unique card names in the collection"""
        unique_cards = list(set([doc['cardName'] for doc in self.documents]))
        return sorted(unique_cards)
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        if not self.documents:
            return {"total_documents": 0, "cards": [], "sections": []}
        
        sections = [doc['section'] for doc in self.documents]
        unique_sections = list(set(sections))
        
        return {
            "total_documents": len(self.documents),
            "cards": self.get_available_cards(),
            "sections": sorted(unique_sections),
            "indexed": self.is_indexed,
            "embeddings_available": len([e for e in self.embeddings if e is not None])
        }
    
    def _extract_card_name(self, filename: str) -> str:
        """Extract and format card name from filename"""
        return filename.replace('.json', '').replace('-', ' ').title()
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return np.dot(a, b) / (norm_a * norm_b)
    
    def _apply_keyword_boost(self, doc: Dict, similarity: float, keywords: List[str]) -> float:
        """Apply keyword-based boosting to similarity score"""
        boost_amount = 0.0
        
        # Check for keywords in section names
        for keyword in keywords:
            if keyword.lower() in doc['section'].lower():
                boost_amount += 0.1
        
        return min(similarity + boost_amount, 1.0)  # Cap at 1.0