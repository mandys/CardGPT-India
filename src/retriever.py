"""
Document Retrieval Service
Handles vector search, document storage, and similarity calculations
Now using ChromaDB for improved search and diversity
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


# --- ADVANCED SEMANTIC CHUNKING LOGIC ---

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
    """Service for storing documents and performing vector similarity search with ChromaDB"""
    
    def __init__(self, openai_api_key: str):
        """Initialize the document retriever with ChromaDB"""
        # Initialize ChromaDB client (persistent storage)
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create embedding function using OpenAI
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name="text-embedding-3-small"
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="credit_card_docs",
            embedding_function=self.embedding_function
        )
        
        self.is_indexed = self.collection.count() > 0
        logger.info(f"ChromaDB initialized with {self.collection.count()} existing documents")
    
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
        return all_chunks
    
    def store_documents(self, documents: List[Dict]):
        """Store documents in ChromaDB (embeddings generated automatically)"""
        if not documents:
            logger.warning("No documents to store")
            return
        
        # Clear existing collection if re-indexing
        try:
            self.collection.delete()
        except:
            pass
        
        # Prepare data for ChromaDB
        doc_ids = [doc['id'] for doc in documents]
        doc_contents = [doc['content'] for doc in documents]
        doc_metadatas = [
            {
                'cardName': doc['cardName'],
                'section': doc['section'],
                'source_file': doc.get('metadata', {}).get('source_file', ''),
                'chunk_type': doc.get('metadata', {}).get('chunk_type', 'semantic')
            }
            for doc in documents
        ]
        
        # Add documents to ChromaDB (embeddings generated automatically)
        self.collection.add(
            documents=doc_contents,
            metadatas=doc_metadatas,
            ids=doc_ids
        )
        
        self.is_indexed = True
        logger.info(f"Stored {len(documents)} documents in ChromaDB")
    
    def search_similar_documents(
        self, 
        query_text: str, 
        top_k: int = 5,
        card_filter: Optional[str] = None,
        use_mmr: bool = True
    ) -> List[Dict]:
        """
        Search for documents similar to the query using ChromaDB with MMR support.
        
        Args:
            query_text: The search query text
            top_k: Number of top results to return
            card_filter: Filter by specific card name
            use_mmr: Use Maximal Marginal Relevance for diversity
            
        Returns:
            List of similar documents with similarity scores
        """
        if not self.is_indexed:
            raise ValueError("Documents not indexed. Call store_documents first.")
        
        # Build where clause for filtering with case-insensitive matching
        where_clause = None
        if card_filter:
            # Find matching card name (case-insensitive)
            available_cards = self.get_available_cards()
            matching_card = None
            for card in available_cards:
                if card.lower() == card_filter.lower():
                    matching_card = card
                    break
            
            if matching_card:
                where_clause = {"cardName": matching_card}
                logger.info(f"Filtering search to card: {matching_card} (matched from: {card_filter})")
            else:
                logger.warning(f"No matching card found for filter: {card_filter}. Available: {available_cards}")
        
        # Perform search with ChromaDB
        # Note: ChromaDB's MMR is still experimental, so we'll implement diversity manually
        search_k = top_k * 3 if use_mmr else top_k  # Get more candidates for MMR
        
        results = self.collection.query(
            query_texts=[query_text],
            n_results=search_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results['documents'][0]:
            logger.warning("No documents found for query")
            return []
        
        # Process results
        processed_results = []
        for doc_content, metadata, distance in zip(
            results['documents'][0], results['metadatas'][0], results['distances'][0]
        ):
            processed_results.append({
                'content': doc_content,
                'cardName': metadata['cardName'],
                'section': metadata['section'],
                'similarity': 1 - distance,  # Convert distance to similarity
                'metadata': metadata
            })
        
        # Apply MMR if requested
        if use_mmr and len(processed_results) > top_k:
            processed_results = self._apply_mmr_diversity(processed_results, top_k)
        else:
            processed_results = processed_results[:top_k]
        
        logger.info(f"Found {len(processed_results)} similar documents")
        return processed_results
    
    def get_available_cards(self) -> List[str]:
        """Get list of unique card names in the collection"""
        if not self.is_indexed:
            return []
        
        # Get all documents to extract unique card names
        all_docs = self.collection.get()
        unique_cards = list(set([
            metadata['cardName'] 
            for metadata in all_docs['metadatas']
        ]))
        return sorted(unique_cards)
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        if not self.is_indexed:
            return {"total_documents": 0, "cards": [], "sections": []}
        
        all_docs = self.collection.get()
        unique_sections = list(set([
            metadata['section'] 
            for metadata in all_docs['metadatas']
        ]))
        
        return {
            "total_documents": self.collection.count(),
            "cards": self.get_available_cards(),
            "sections": sorted(unique_sections),
            "indexed": self.is_indexed,
            "embeddings_available": self.collection.count()
        }
    
    def _extract_card_name(self, filename: str) -> str:
        """Extract and format card name from filename"""
        return filename.replace('.json', '').replace('-', ' ').title()
    
    def _apply_mmr_diversity(self, results: List[Dict], top_k: int, diversity_weight: float = 0.5) -> List[Dict]:
        """
        Apply Maximal Marginal Relevance to promote diversity in results.
        
        Args:
            results: List of search results with similarity scores
            top_k: Number of results to return
            diversity_weight: Weight for diversity vs relevance (0.0 = pure relevance, 1.0 = pure diversity)
        
        Returns:
            Diversified list of results
        """
        if len(results) <= top_k:
            return results
        
        selected = []
        remaining = results.copy()
        
        # Select the most relevant document first
        best_doc = max(remaining, key=lambda x: x['similarity'])
        selected.append(best_doc)
        remaining.remove(best_doc)
        
        # Select remaining documents balancing relevance and diversity
        while len(selected) < top_k and remaining:
            best_score = -1
            best_doc = None
            
            for doc in remaining:
                relevance = doc['similarity']
                
                # Calculate diversity (minimum similarity to selected docs)
                diversity = self._calculate_diversity(doc, selected)
                
                # MMR score
                mmr_score = (1 - diversity_weight) * relevance + diversity_weight * diversity
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_doc = doc
            
            if best_doc:
                selected.append(best_doc)
                remaining.remove(best_doc)
        
        logger.info(f"Applied MMR diversity: {len(selected)} documents selected")
        return selected
    
    def _calculate_diversity(self, doc: Dict, selected_docs: List[Dict]) -> float:
        """
        Calculate diversity score for a document against selected documents.
        
        Args:
            doc: Candidate document
            selected_docs: Already selected documents
            
        Returns:
            Diversity score (higher = more diverse)
        """
        if not selected_docs:
            return 1.0
        
        # Simple diversity based on card name and section
        max_diversity = 0.0
        
        for selected in selected_docs:
            diversity = 0.0
            
            # Different card = more diverse
            if doc['cardName'] != selected['cardName']:
                diversity += 0.5
            
            # Different section = more diverse
            if doc['section'] != selected['section']:
                diversity += 0.3
            
            # Content-based diversity (simple word overlap)
            content_diversity = self._calculate_content_diversity(doc['content'], selected['content'])
            diversity += content_diversity * 0.2
            
            max_diversity = max(max_diversity, diversity)
        
        return min(max_diversity, 1.0)
    
    def _calculate_content_diversity(self, content1: str, content2: str) -> float:
        """Calculate content diversity between two text strings"""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 1.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard_similarity = len(intersection) / len(union)
        return 1 - jaccard_similarity  # Higher diversity = lower similarity
    
    # Legacy method for backward compatibility
    def store_documents_and_embeddings(self, documents: List[Dict], embeddings: List[List[float]]):
        """Legacy method - now delegates to store_documents"""
        logger.warning("store_documents_and_embeddings is deprecated. Use store_documents instead.")
        # embeddings parameter is ignored since ChromaDB handles embedding generation
        self.store_documents(documents)