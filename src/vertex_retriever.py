# In src/vertex_retriever.py

import time
import json
import logging
from typing import List, Dict, Optional
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core import exceptions as google_exceptions
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)

class VertexRetriever:
    """
    (Simplified & Corrected) Vertex AI Search retriever.
    Focuses on robust filtering and clean response parsing.
    """
    def __init__(self, project_id: str, location: str, data_store_id: str):
        self.project_id = project_id
        self.location = location
        self.data_store_id = data_store_id
        self.client = discoveryengine.SearchServiceClient()
        self.serving_config = self.client.serving_config_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            serving_config="default_config",
        )
        logger.info(f"Vertex AI Search client initialized for project: {project_id}")

    def search_similar_documents(self, query_text: str, card_filter: Optional[str] = None, top_k: int = 7, use_mmr: bool = False) -> List[Dict]:
        """Performs a search with precise metadata filtering."""
        # Note: use_mmr is ignored for Vertex AI Search (ChromaDB-specific parameter)
        
        # For now, disable filtering since the data store schema needs to be updated
        # TODO: Re-enable filtering once the data store is updated with new JSONL format
        if card_filter:
            logger.info(f"Card filter '{card_filter}' requested but filtering disabled (data store needs update)")
            # Enhance query with card name instead of using filter
            enhanced_query = f"{card_filter} {query_text}"
        else:
            enhanced_query = query_text
            
        logger.info(f"Executing search with enhanced query: {enhanced_query}")
        
        request = discoveryengine.SearchRequest(
            serving_config=self.serving_config,
            query=enhanced_query,
            page_size=top_k,
            # filter=filter_str  # Disabled until data store update
            # Explicitly request document content
            content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
                snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                    return_snippet=True,
                    max_snippet_count=3
                ),
                extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                    max_extractive_answer_count=3,
                    max_extractive_segment_count=3
                )
            )
        )
        
        try:
            response = self.client.search(request)
            results = self._process_response(response)
            
            # If card_filter is specified, post-process results to filter by card name
            if card_filter and results:
                filtered_results = []
                for result in results:
                    card_name = result.get('cardName', '')
                    # More flexible matching
                    if (card_filter.lower() in card_name.lower() or 
                        any(word in card_name.lower() for word in card_filter.lower().split())):
                        filtered_results.append(result)
                
                logger.info(f"Post-filtered results: {len(filtered_results)}/{len(results)} documents match '{card_filter}'")
                return filtered_results[:top_k]
            
            return results
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Vertex AI Search API error: {e}")
            return self._fallback_response(query_text)

    def _process_response(self, response: discoveryengine.SearchResponse) -> List[Dict]:
        """(Simplified & Corrected) Processes the search response."""
        processed_results = []
        
        logger.info(f"=== DEBUGGING VERTEX AI RESPONSE ===")
        logger.info(f"Total results: {len(response.results)}")
        
        for i, result in enumerate(response.results):
            logger.info(f"\n--- RESULT {i+1} ---")
            
            # Convert the complex result object into a simple dictionary
            result_dict = MessageToDict(result._pb)
            logger.info(f"Result dict keys: {list(result_dict.keys())}")
            
            # Extract the data cleanly and directly
            document = result_dict.get('document', {})
            logger.info(f"Document keys: {list(document.keys())}")
            
            struct_data = document.get('structData', {})
            logger.info(f"Struct data: {struct_data}")
            
            # Also check derivedStructData
            derived_struct_data = document.get('derivedStructData', {})
            logger.info(f"Derived struct data keys: {list(derived_struct_data.keys())}")
            logger.info(f"Derived struct data: {derived_struct_data}")
            
            # Handle both text and raw_bytes content formats
            content_obj = document.get('content', {})
            logger.info(f"Content object keys: {list(content_obj.keys())}")
            logger.info(f"Content object: {content_obj}")
            
            content = ''
            
            # Priority 1: Check document.content for raw content
            if 'text' in content_obj:
                content = content_obj['text']
                logger.info(f"Found 'text' field, length: {len(content)}")
                logger.info(f"Text content preview: {content[:200]}...")
            elif 'rawBytes' in content_obj:
                # Decode Base64 content
                import base64
                try:
                    raw_bytes = content_obj['rawBytes']
                    logger.info(f"Found 'rawBytes' field, length: {len(raw_bytes)}")
                    content_bytes = base64.b64decode(raw_bytes)
                    content = content_bytes.decode('utf-8')
                    logger.info(f"Successfully decoded Base64, content length: {len(content)}")
                    logger.info(f"Decoded content preview: {content[:200]}...")
                except Exception as e:
                    logger.error(f"Failed to decode Base64 content: {e}")
                    content = "Content decoding failed"
                    
            # Priority 2: If no raw content, extract from Vertex AI's processed fields
            if not content and derived_struct_data:
                logger.info(f"No raw content found, extracting from derivedStructData...")
                
                # Try extractive_segments first (most complete)
                if 'extractive_segments' in derived_struct_data:
                    segments = derived_struct_data['extractive_segments']
                    if segments and isinstance(segments, list):
                        segment_texts = []
                        for segment in segments:
                            if isinstance(segment, dict) and 'content' in segment:
                                segment_texts.append(segment['content'])
                        
                        if segment_texts:
                            content = '\n\n'.join(segment_texts)
                            logger.info(f"Extracted from extractive_segments, length: {len(content)}")
                            logger.info(f"Segments content preview: {content[:200]}...")
                
                # Fallback to extractive_answers
                if not content and 'extractive_answers' in derived_struct_data:
                    answers = derived_struct_data['extractive_answers']
                    if answers and isinstance(answers, list):
                        answer_texts = []
                        for answer in answers:
                            if isinstance(answer, dict) and 'content' in answer:
                                answer_texts.append(answer['content'])
                        
                        if answer_texts:
                            content = '\n\n'.join(answer_texts)
                            logger.info(f"Extracted from extractive_answers, length: {len(content)}")
                            logger.info(f"Answers content preview: {content[:200]}...")
            
            if not content:
                logger.warning(f"No content found in any field!")
                logger.info(f"Available content fields: {list(content_obj.keys())}")
                logger.info(f"Available derived fields: {list(derived_struct_data.keys())}")
            
            card_name = struct_data.get('cardName', 'Unknown Card')
            section = struct_data.get('section', 'details')
            
            logger.info(f"Final extracted: cardName='{card_name}', section='{section}', content_length={len(content)}")
            
            processed_results.append({
                'content': content,
                'cardName': card_name,
                'section': section,
                'similarity': result_dict.get('relevanceScore', 0.8),
            })
        
        logger.info(f"=== END DEBUGGING ===")
        logger.info(f"Successfully processed {len(processed_results)} documents.")
        return processed_results
        
    def get_available_cards(self) -> List[str]:
        """Returns the list of available credit cards."""
        return [
            "Axis Atlas",
            "ICICI EPM", 
            "HSBC Premier"
        ]

    def _fallback_response(self, query: str) -> List[Dict]:
        """Provides a fallback response on API failure."""
        logger.warning(f"Using fallback response for query: {query}")
        return [{
            'content': f"Search is temporarily unavailable for your query: '{query}'. Please check logs.",
            'cardName': "System",
            'section': "Error",
            'similarity': 0.0
        }]