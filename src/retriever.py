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


class DocumentRetriever:
    """Service for storing documents and performing vector similarity search"""
    
    def __init__(self):
        """Initialize the document retriever"""
        self.documents: List[Dict] = []
        self.embeddings: List[Optional[List[float]]] = []
        self.is_indexed = False
    
    def load_documents_from_json(self, data_directory: str = "data") -> List[Dict]:
        """
        Load and process credit card documents from JSON files
        
        Args:
            data_directory: Directory containing JSON files
            
        Returns:
            List of processed documents
        """
        data_path = Path(data_directory)
        
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path.absolute()}")
        
        json_files = list(data_path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"No JSON files found in {data_path}")
        
        documents = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    card_data = json.load(f)
                    card_name = self._extract_card_name(json_file.name)
                    
                    # Process common_terms
                    if 'common_terms' in card_data:
                        for section, data in card_data['common_terms'].items():
                            content = self._format_section_content(section, data)
                            documents.append({
                                "id": f"{card_name}_common_{section}",
                                "cardName": card_name,
                                "content": content,
                                "section": f"common_terms_{section}",
                                "metadata": {
                                    "section": f"common_terms_{section}",
                                    "cardType": card_name,
                                    "source_file": json_file.name
                                }
                            })
                    
                    # Process card-specific data
                    if 'card' in card_data:
                        card_info = card_data['card']
                        for section, data in card_info.items():
                            if self._should_process_section(section, data):
                                content = self._format_section_content(section, data)
                                documents.append({
                                    "id": f"{card_name}_card_{section}",
                                    "cardName": card_name,
                                    "content": content,
                                    "section": section,
                                    "metadata": {
                                        "section": section,
                                        "cardType": card_name,
                                        "source_file": json_file.name
                                    }
                                })
            
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
                continue
        
        logger.info(f"Loaded {len(documents)} documents from {len(json_files)} files")
        return documents
    
    def store_documents_and_embeddings(self, documents: List[Dict], embeddings: List[List[float]]):
        """Store documents and their corresponding embeddings"""
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        self.documents = documents
        self.embeddings = embeddings
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
        Search for documents similar to the query embedding
        
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
        
        # Filter documents if card_filter is specified
        if card_filter:
            doc_indices = [i for i, doc in enumerate(self.documents) 
                          if doc['cardName'].lower() == card_filter.lower()]
        else:
            doc_indices = list(range(len(self.documents)))
        
        # Calculate similarities
        similarities = []
        for idx in doc_indices:
            doc = self.documents[idx]
            doc_embedding = self.embeddings[idx]
            
            if doc_embedding is None:
                continue
            
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            
            # Apply keyword boosting if specified
            if boost_keywords:
                similarity = self._apply_keyword_boost(doc, similarity, boost_keywords)
            
            if similarity >= threshold:
                similarities.append((similarity, idx))
        
        # Sort by similarity and get top results
        similarities.sort(reverse=True)
        top_results = similarities[:top_k]
        
        # Build result documents
        results = []
        for similarity, idx in top_results:
            doc = self.documents[idx].copy()
            doc["similarity"] = similarity
            results.append(doc)
        
        logger.info(f"Found {len(results)} similar documents (threshold: {threshold})")
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
    
    def _should_process_section(self, section: str, data: Any) -> bool:
        """Determine if a section should be processed as a document"""
        # Skip metadata fields
        skip_sections = ["id", "name", "bank", "category", "network", "launch_date"]
        if section in skip_sections:
            return False
        
        # Include important sections regardless of type
        important_sections = ["fees", "rewards", "reward_capping", "milestones", "insurance", "lounge_access", "welcome_benefits"]
        if section in important_sections:
            return True
        
        # Include if it's a dictionary with meaningful content
        return isinstance(data, dict) and data
    
    def _format_section_content(self, section: str, data: Any) -> str:
        """Format section data into readable content"""
        section_title = section.replace('_', ' ').title()
        content = f"{section_title}:\n"
        
        if isinstance(data, dict):
            for key, value in data.items():
                key_formatted = key.replace('_', ' ').title()
                if isinstance(value, dict):
                    content += f"  {key_formatted}:\n"
                    for sub_key, sub_value in value.items():
                        sub_key_formatted = sub_key.replace('_', ' ').title()
                        if isinstance(sub_value, (list, dict)):
                            content += f"    {sub_key_formatted}: {json.dumps(sub_value, indent=2)}\n"
                        else:
                            content += f"    {sub_key_formatted}: {sub_value}\n"
                elif isinstance(value, list):
                    content += f"  {key_formatted}: {', '.join(map(str, value))}\n"
                else:
                    content += f"  {key_formatted}: {value}\n"
        elif isinstance(data, list):
            content += f"  {', '.join(map(str, data))}\n"
        else:
            content += f"  {data}\n"
        
        return content
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a_np = np.array(a)
        b_np = np.array(b)
        
        norm_a = np.linalg.norm(a_np)
        norm_b = np.linalg.norm(b_np)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return np.dot(a_np, b_np) / (norm_a * norm_b)
    
    def _apply_keyword_boost(self, doc: Dict, similarity: float, keywords: List[str]) -> float:
        """Apply keyword-based boosting to similarity score"""
        boost_amount = 0.0
        
        # Check for keywords in section names
        for keyword in keywords:
            if keyword.lower() in doc['section'].lower():
                boost_amount += 0.1
        
        return min(similarity + boost_amount, 1.0)  # Cap at 1.0