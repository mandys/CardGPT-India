# In src/vertex_retriever.py

import os
import time
import json
import logging
import tempfile
from typing import List, Dict, Optional
from google.cloud import discoveryengine
from google.api_core import exceptions as google_exceptions
from google.protobuf.json_format import MessageToDict
from google.auth import default
from google.oauth2 import service_account

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
        
        # Set up authentication
        credentials = self._get_credentials()
        if credentials:
            self.client = discoveryengine.SearchServiceClient(credentials=credentials)
        else:
            self.client = discoveryengine.SearchServiceClient()
            
        self.serving_config = self.client.serving_config_path(
            project=project_id,
            location=location,
            data_store=data_store_id,
            serving_config="default_config",
        )
        logger.info(f"Vertex AI Search client initialized for project: {project_id}")

    def _get_credentials(self):
        """Get Google Cloud credentials from environment variables or default."""
        try:
            # Check if we have JSON credentials in environment variable
            creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
            if creds_json:
                logger.info("Using GOOGLE_APPLICATION_CREDENTIALS_JSON from environment")
                # Parse the JSON credentials
                creds_info = json.loads(creds_json)
                credentials = service_account.Credentials.from_service_account_info(creds_info)
                return credentials
            
            # Check if GOOGLE_APPLICATION_CREDENTIALS file path is set
            creds_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if creds_file and os.path.exists(creds_file):
                logger.info(f"Using GOOGLE_APPLICATION_CREDENTIALS file: {creds_file}")
                credentials = service_account.Credentials.from_service_account_file(creds_file)
                return credentials
            
            # Try default credentials (local development)
            logger.info("Attempting to use default credentials")
            credentials, _ = default()
            return credentials
            
        except Exception as e:
            logger.warning(f"Failed to load credentials: {e}")
            # Return None to let the client try default auth
            return None

    def search_similar_documents(self, query_text: str, card_filter: Optional[str] = None, top_k: int = 10, use_mmr: bool = False) -> List[Dict]:
        """Performs a search with precise metadata filtering."""
        # Note: use_mmr is ignored for Vertex AI Search (ChromaDB-specific parameter)
        
        # With document-level aliases, we can rely on natural search matching
        # No need for hardcoded card name mappings anymore
        enhanced_query = query_text
        
        # For card filtering, simply add the card name to the query
        if card_filter:
            logger.info(f"Adding card filter '{card_filter}' to query")
            enhanced_query = f"{card_filter} {enhanced_query}"
            
        # Note: Query enhancement is now handled by QueryEnhancer service
        # Vertex retriever focuses on search execution only
        
        logger.info(f"🔍 [SEARCH_DEBUG] === VERTEX AI SEARCH REQUEST ===")
        logger.info(f"🔍 [SEARCH_DEBUG] Original query: '{query_text}'")
        logger.info(f"🔍 [SEARCH_DEBUG] Enhanced query: '{enhanced_query}'")
        logger.info(f"🔍 [SEARCH_DEBUG] Card filter: {card_filter}")
        logger.info(f"🔍 [SEARCH_DEBUG] Top-k: {top_k}")
        logger.info(f"🔍 [SEARCH_DEBUG] Expecting 4 cards: HDFC Infinia, Axis Atlas, ICICI EPM, HSBC Premier")
        
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
            
            return results
            
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Vertex AI Search API error: {e}")
            return self._fallback_response(query_text)

    def _process_response(self, response: discoveryengine.SearchResponse) -> List[Dict]:
        """(Simplified & Corrected) Processes the search response."""
        processed_results = []
        
        logger.info(f"=== DEBUGGING VERTEX AI RESPONSE ===")
        logger.info(f"Total results: {len(response.results)}")
        
        # Track card coverage for debugging missing cards issue
        cards_found = set()
        card_name_mapping = {
            'HDFC Infinia Credit Card': 'HDFC Infinia',
            'Axis Bank Atlas Credit Card': 'Axis Atlas', 
            'ICICI Bank Emeralde Private Metal Credit Card': 'ICICI EPM',
            'HSBC Premier Credit Card': 'HSBC Premier',
            # Handle variations in card names from different data versions
            'Emeralde Private Metal Credit Card': 'ICICI EPM',
            'Axis Atlas Credit Card': 'Axis Atlas',
            'HDFC Infinia': 'HDFC Infinia',
            'HSBC Premier': 'HSBC Premier'
        }
        
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
            # logger.info(f"Derived struct data: {derived_struct_data}")
            
            # Handle both text and raw_bytes content formats
            content_obj = document.get('content', {})
            # logger.info(f"Content object keys: {list(content_obj.keys())}")
            # logger.info(f"Content object: {content_obj}")
            
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
                
                # Collect all available content from multiple sources
                all_content_parts = []
                
                # Extract from extractive_segments (most complete)
                if 'extractive_segments' in derived_struct_data:
                    segments = derived_struct_data['extractive_segments']
                    if segments and isinstance(segments, list):
                        for segment in segments:
                            if isinstance(segment, dict) and 'content' in segment:
                                all_content_parts.append(segment['content'])
                        logger.info(f"Extracted {len(all_content_parts)} segments from extractive_segments")
                
                # ALSO extract from extractive_answers (contains specific information like golf benefits)
                if 'extractive_answers' in derived_struct_data:
                    answers = derived_struct_data['extractive_answers']
                    if answers and isinstance(answers, list):
                        for answer in answers:
                            if isinstance(answer, dict) and 'content' in answer:
                                # Only add if not already present to avoid duplicates
                                answer_content = answer['content']
                                if answer_content not in all_content_parts:
                                    all_content_parts.append(answer_content)
                        logger.info(f"Added {len([a for a in answers if isinstance(a, dict) and 'content' in a])} answers from extractive_answers")
                
                # Combine all content parts
                if all_content_parts:
                    content = '\n\n'.join(all_content_parts)
                    logger.info(f"Combined content from multiple sources, total length: {len(content)}")
                    logger.info(f"Combined content preview: {content[:200]}...")
                    
            
            if not content:
                logger.warning(f"No content found in any field!")
                logger.info(f"Available content fields: {list(content_obj.keys())}")
                logger.info(f"Available derived fields: {list(derived_struct_data.keys())}")
            
            card_name = struct_data.get('cardName', 'Unknown Card')
            section = struct_data.get('section', 'details')
            
            # Track which cards are found for coverage analysis
            if card_name in card_name_mapping:
                cards_found.add(card_name_mapping[card_name])
                logger.info(f"✅ [CARD_TRACKING] Found {card_name_mapping[card_name]} data")
            elif card_name != 'Unknown Card':
                logger.warning(f"⚠️ [CARD_TRACKING] Found unmapped card: {card_name}")
            
            logger.info(f"Final extracted: cardName='{card_name}', section='{section}', content_length={len(content)}")
            
            processed_results.append({
                'content': content,
                'cardName': card_name,
                'section': section,
                'similarity': result_dict.get('relevanceScore', 0.8),
            })
        
        # Card coverage analysis - critical for debugging missing card issue
        all_expected_cards = set(['HDFC Infinia', 'Axis Atlas', 'ICICI EPM', 'HSBC Premier'])
        missing_cards = all_expected_cards - cards_found
        
        logger.info(f"=== CARD COVERAGE ANALYSIS ===")
        logger.info(f"🎯 [COVERAGE] Cards found in results: {sorted(list(cards_found))}")
        if missing_cards:
            logger.warning(f"❌ [COVERAGE] Missing cards: {sorted(list(missing_cards))}")
            logger.warning(f"🚨 [COVERAGE] CRITICAL: ICICI EPM missing from search results!" if 'ICICI EPM' in missing_cards else "")
        else:
            logger.info(f"✅ [COVERAGE] All 4 cards present in search results!")
        logger.info(f"📊 [COVERAGE] Card coverage: {len(cards_found)}/4 cards ({len(cards_found)/4*100:.1f}%)")
        
        logger.info(f"=== END DEBUGGING ===")
        logger.info(f"Successfully processed {len(processed_results)} documents.")
        return processed_results
        
    # def get_available_cards(self) -> List[str]:
    #     """Returns the list of available credit cards."""
    #     return [
    #         "Axis Atlas",
    #         "ICICI EPM", 
    #         "HSBC Premier"
    #     ]

    

    def _fallback_response(self, query: str) -> List[Dict]:
        """Provides a fallback response on API failure."""
        logger.warning(f"Using fallback response for query: {query}")
        return [{
            'content': f"Search is temporarily unavailable for your query: '{query}'. Please check logs.",
            'cardName': "System",
            'section': "Error",
            'similarity': 0.0
        }]