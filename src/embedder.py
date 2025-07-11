"""
OpenAI Embedding Service
Handles text-to-vector conversion using OpenAI's embedding models
"""

import openai
import streamlit as st
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing OpenAI embeddings"""
    
    def __init__(self, api_key: str):
        """Initialize the embedding service with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "text-embedding-3-small"
        self.cost_per_1k_tokens = 0.00002  # $0.00002 per 1K tokens
    
    def generate_single_embedding(self, text: str) -> tuple[List[float], Dict[str, Any]]:
        """
        Generate embedding for a single text
        
        Returns:
            tuple: (embedding_vector, usage_info)
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format='float'
            )
            
            embedding = response.data[0].embedding
            usage = {
                "tokens": response.usage.total_tokens,
                "cost": response.usage.total_tokens * self.cost_per_1k_tokens / 1000,
                "model": self.model
            }
            
            return embedding, usage
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise e
    
    def generate_batch_embeddings(self, documents: List[Dict], use_batch_api: bool = True) -> tuple[List[List[float]], Dict[str, Any]]:
        """
        Generate embeddings for multiple documents
        
        Args:
            documents: List of document dictionaries with 'content' field
            use_batch_api: Whether to use OpenAI's batch API (recommended)
            
        Returns:
            tuple: (embeddings_list, total_usage_info)
        """
        if use_batch_api and len(documents) <= 2048:
            return self._generate_batch_embeddings_optimized(documents)
        else:
            return self._generate_batch_embeddings_individual(documents)
    
    def _generate_batch_embeddings_optimized(self, documents: List[Dict]) -> tuple[List[List[float]], Dict[str, Any]]:
        """Generate embeddings using OpenAI's batch API (much faster)"""
        try:
            # Extract all content
            all_content = [doc['content'] for doc in documents]
            
            # Show progress
            if 'streamlit' in globals():
                st.write(f"🚀 Generating embeddings for {len(documents)} documents in batch...")
            
            # Single API call for all documents
            response = self.client.embeddings.create(
                model=self.model,
                input=all_content,
                encoding_format='float'
            )
            
            # Extract embeddings
            embeddings = [data.embedding for data in response.data]
            
            total_usage = {
                "total_tokens": response.usage.total_tokens,
                "total_cost": response.usage.total_tokens * self.cost_per_1k_tokens / 1000,
                "successful_embeddings": len(embeddings),
                "failed_embeddings": 0,
                "model": self.model,
                "api_calls": 1
            }
            
            logger.info(f"Generated {len(embeddings)} embeddings in single batch API call")
            return embeddings, total_usage
            
        except Exception as e:
            logger.error(f"Batch embedding failed, falling back to individual calls: {str(e)}")
            return self._generate_batch_embeddings_individual(documents)
    
    def _generate_batch_embeddings_individual(self, documents: List[Dict]) -> tuple[List[List[float]], Dict[str, Any]]:
        """Generate embeddings using individual API calls (legacy method)"""
        embeddings = []
        total_tokens = 0
        successful_count = 0
        
        if 'streamlit' in globals():
            st.write(f"⚠️ Using individual API calls for {len(documents)} documents...")
        
        for i, doc in enumerate(documents):
            try:
                embedding, usage = self.generate_single_embedding(doc['content'])
                embeddings.append(embedding)
                total_tokens += usage['tokens']
                successful_count += 1
                
                # Show progress in Streamlit
                if 'streamlit' in globals():
                    if i % 10 == 0:  # Update every 10 documents
                        st.write(f"Generated embeddings for {i+1}/{len(documents)} documents...")
                        
            except Exception as e:
                logger.error(f"Error generating embedding for document {doc.get('id', i)}: {str(e)}")
                embeddings.append(None)  # Placeholder for failed embedding
        
        total_usage = {
            "total_tokens": total_tokens,
            "total_cost": total_tokens * self.cost_per_1k_tokens / 1000,
            "successful_embeddings": successful_count,
            "failed_embeddings": len(documents) - successful_count,
            "model": self.model,
            "api_calls": len(documents)
        }
        
        logger.info(f"Generated {successful_count}/{len(documents)} embeddings using individual API calls")
        return embeddings, total_usage
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model"""
        return {
            "model": self.model,
            "dimensions": 1536,  # text-embedding-3-small dimensions
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "max_input_tokens": 8191
        }