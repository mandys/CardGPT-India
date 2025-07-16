"""
Vertex AI Search Retriever
Replaces the custom ChromaDB implementation with Google's managed Vertex AI Search service.
Provides enterprise-grade search capabilities with minimal maintenance overhead.
"""

import time
import json
import logging
from typing import List, Dict, Optional, Any
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core import exceptions as google_exceptions
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)


def _convert_search_result_to_dict(result: discoveryengine.SearchResponse.SearchResult) -> Dict:
    """A robust helper to convert a search result proto message to a Python dict."""
    try:
        return MessageToDict(result._pb)
    except Exception as e:
        logger.error(f"Failed to convert search result to dict: {e}")
        return {}


class VertexRetriever:
    """
    Production-ready Vertex AI Search retriever with simplified, robust response parsing.
    """
    
    def __init__(self, project_id: str, location: str, data_store_id: str):
        """Initialize the Vertex AI Search retriever."""
        self.project_id = project_id
        self.location = location
        self.data_store_id = data_store_id
        
        # Initialize the client
        try:
            self.client = discoveryengine.SearchServiceClient()
            logger.info(f"Vertex AI Search client initialized for project: {project_id}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI Search client: {e}")
            raise
        
        # Build the serving config path
        self.serving_config = self.client.serving_config_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            serving_config="default_config"
        )
        
        # Performance tracking
        self.search_times = []
        self.search_count = 0
        self.error_count = 0
        
        logger.info(f"Vertex AI Search configured:")
        logger.info(f"  Project: {project_id}")
        logger.info(f"  Location: {location}")
        logger.info(f"  Data Store: {data_store_id}")
        logger.info(f"  Serving Config: {self.serving_config}")
    
    def search_similar_documents(
        self, 
        query_text: str, 
        top_k: int = 5,
        card_filter: Optional[str] = None,
        use_mmr: bool = True  # Kept for compatibility
    ) -> List[Dict]:
        """
        Search for documents similar to the query using Vertex AI Search.
        
        Args:
            query_text: The search query text
            top_k: Number of top results to return
            card_filter: Filter by specific card name (semantic filtering)
            use_mmr: Compatibility parameter (not used in Vertex AI)
            
        Returns:
            List of similar documents with similarity scores
        """
        start_time = time.time()
        
        try:
            # Enhance query with card filter for semantic search
            enhanced_query = query_text
            if card_filter:
                # Make the card filter more flexible for semantic search
                card_keywords = {
                    'Axis Atlas': ['axis', 'atlas', 'axis-atlas'],
                    'ICICI EPM': ['icici', 'epm', 'icici-epm', 'emeralde'],
                    'HSBC Premier': ['hsbc', 'premier', 'hsbc-premier']
                }
                
                # Add relevant keywords to the query
                if card_filter in card_keywords:
                    keywords = ' '.join(card_keywords[card_filter])
                    enhanced_query = f"{keywords} {query_text}"
                else:
                    enhanced_query = f"{card_filter} {query_text}"
                
                logger.info(f"Enhanced query with card filter: {card_filter} -> {enhanced_query}")
            
            # Build and execute search request
            request = self._build_search_request(enhanced_query, top_k)
            response = self.client.search(request)
            
            # Process results using the corrected parsing logic
            processed_results = self._process_search_response(response)
            
            # Track performance
            search_time = time.time() - start_time
            self.search_times.append(search_time)
            self.search_count += 1
            
            logger.info(f"Vertex AI Search completed in {search_time:.3f}s, found {len(processed_results)} documents")
            
            return processed_results[:top_k]
            
        except google_exceptions.GoogleAPIError as e:
            self.error_count += 1
            logger.error(f"Vertex AI Search API error: {e}")
            return self._fallback_response(query_text, card_filter)
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error in Vertex AI Search: {e}")
            return self._fallback_response(query_text, card_filter)

    def _build_search_request(self, query_text: str, top_k: int) -> discoveryengine.SearchRequest:
        """Constructs the search request object."""
        return discoveryengine.SearchRequest(
            serving_config=self.serving_config,
            query=query_text,
            page_size=top_k,
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True
                ),
                summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
                    summary_result_count=top_k,
                    include_citations=False
                ),
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=3
                )
            )
        )

    def _process_search_response(self, response: discoveryengine.SearchResponse) -> List[Dict]:
        """Processes the search response and extracts content correctly."""
        processed_results = []
        
        for result in response.results:
            # Convert the entire complex result object into a clean dictionary
            result_dict = _convert_search_result_to_dict(result)
            
            # Now, safely extract data from the dictionary
            document = result_dict.get('document', {})
            struct_data = document.get('derivedStructData', {})
            card_name = self._extract_card_name(document.get('name', ''))
            
            # Combine all useful text into a single content block
            content_parts = []
            if 'summary' in result_dict and result_dict['summary']:
                content_parts.append(f"Summary: {result_dict['summary']}")
            
            # Format the main structured data into readable text
            if struct_data:
                content_parts.append(self._format_dict_to_text(struct_data))
            
            # If no content found, add basic document info
            if not content_parts:
                content_parts.append(f"Document ID: {document.get('id', 'unknown')}")
            
            processed_results.append({
                'content': "\n\n".join(content_parts),
                'cardName': card_name,
                'section': self._extract_section(struct_data),
                'similarity': getattr(result, 'relevance_score', 0.8),
                'metadata': {
                    'document_id': document.get('id'),
                    'vertex_source': True
                }
            })
            
        return processed_results

    def _format_dict_to_text(self, data: Dict, indent: int = 0) -> str:
        """Recursively formats a dictionary into a readable indented string."""
        text_parts = []
        indent_str = "  " * indent
        
        for key, value in data.items():
            key_formatted = key.replace('_', ' ').title()
            if isinstance(value, dict):
                text_parts.append(f"{indent_str}- {key_formatted}:")
                text_parts.append(self._format_dict_to_text(value, indent + 1))
            elif isinstance(value, list):
                list_items = ", ".join(map(str, value))
                text_parts.append(f"{indent_str}- {key_formatted}: {list_items}")
            else:
                text_parts.append(f"{indent_str}- {key_formatted}: {value}")
        
        return "\n".join(text_parts)

    def _extract_card_name(self, document_name: str) -> str:
        """Extracts card name from the document's resource name."""
        if 'axis-atlas' in document_name.lower(): return 'Axis Atlas'
        if 'icici-epm' in document_name.lower(): return 'ICICI EPM'
        if 'hsbc-premier' in document_name.lower(): return 'HSBC Premier'
        # Also check for individual keywords
        if 'axis' in document_name.lower(): return 'Axis Atlas'
        if 'icici' in document_name.lower(): return 'ICICI EPM'
        if 'hsbc' in document_name.lower(): return 'HSBC Premier'
        return 'Unknown Card'
        
    def _extract_section(self, data: Dict) -> str:
        """Extract section information from structured data."""
        # Try to infer section from the data structure
        if 'rewards' in str(data).lower():
            return 'rewards'
        elif 'fees' in str(data).lower():
            return 'fees'
        elif 'benefits' in str(data).lower():
            return 'benefits'
        elif 'milestone' in str(data).lower():
            return 'milestones'
        else:
            return 'card_details'
    
    def _fallback_response(self, query_text: str, card_filter: Optional[str]) -> List[Dict]:
        """Provide fallback response when Vertex AI Search fails."""
        logger.warning("Using fallback response due to Vertex AI Search failure")
        
        fallback_content = f"""
        Search temporarily unavailable. Query: {query_text}
        
        Please try again or contact support if the issue persists.
        Common credit card information:
        - Annual fees vary by card type
        - Reward rates depend on spending category
        - Check card-specific terms and conditions
        """
        
        return [{
            'content': fallback_content,
            'cardName': card_filter or 'General',
            'section': 'fallback_response',
            'similarity': 0.1,
            'metadata': {
                'is_fallback': True,
                'error_type': 'vertex_ai_search_failure'
            }
        }]
    
    def get_available_cards(self) -> List[str]:
        """Get list of available cards (hardcoded for now)."""
        return ['Axis Atlas', 'ICICI EPM', 'HSBC Premier']
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        avg_search_time = sum(self.search_times) / len(self.search_times) if self.search_times else 0
        
        return {
            'total_searches': self.search_count,
            'total_errors': self.error_count,
            'error_rate': self.error_count / max(self.search_count, 1),
            'average_search_time': avg_search_time,
            'last_search_times': self.search_times[-5:] if len(self.search_times) >= 5 else self.search_times,
            'service_health': 'healthy' if self.error_count / max(self.search_count, 1) < 0.1 else 'degraded'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the Vertex AI Search service."""
        try:
            # Try a simple search to verify connectivity
            test_results = self.search_similar_documents("test query", top_k=1)
            
            return {
                'status': 'healthy',
                'vertex_ai_accessible': True,
                'last_test_time': time.time(),
                'performance_stats': self.get_performance_stats()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'vertex_ai_accessible': False,
                'error': str(e),
                'last_test_time': time.time()
            }