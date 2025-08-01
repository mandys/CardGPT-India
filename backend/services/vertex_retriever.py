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
            
        # Special enhancement for insurance spending queries
        if "insurance" in query_text.lower() and any(word in query_text.lower() for word in ["spend", "spending", "spends", "earn", "points", "rewards"]):
            enhanced_query += " earning rates reward capping others section insurance transactions"
            logger.info(f"Enhanced insurance spending query: {enhanced_query}")
        
        # Special enhancement for fee waiver queries
        if any(term in query_text.lower() for term in ["fee waiver", "waiver", "annual fee waiver"]):
            enhanced_query += " fee_waiver annual fee spend threshold spend condition"
            logger.info(f"Enhanced fee waiver query: {enhanced_query}")
        
        # Special enhancement for education spending queries
        if "education" in query_text.lower() and any(word in query_text.lower() for word in ["points", "rewards", "earn", "spending", "fee", "payment"]):
            # With aliases, we just need to add relevant terms for better matching
            enhanced_query += " education education_government rewards rate points MCC earning"
            logger.info(f"Enhanced education spending query: {enhanced_query}")
        
        # Special enhancement for travel queries
        travel_keywords = ["travel", "trip", "vacation", "holiday", "journey", "lot of travel", "upcoming travel", "business travel"]
        if any(keyword in query_text.lower() for keyword in travel_keywords):
            # Add travel-specific terms for better matching
            enhanced_query += " travel benefits lounge access insurance miles points rewards foreign currency charges welcome bonus"
            logger.info(f"Enhanced travel query: {enhanced_query}")
        
        # Special enhancement for generic recommendation queries
        generic_rec_keywords = ["which card should i", "best card for", "recommend", "suggest", "better card", "good card", "right card"]
        if any(keyword in query_text.lower() for keyword in generic_rec_keywords) and not card_filter:
            # Add comparison terms for better matching
            enhanced_query += " comparison benefits features rewards"
            logger.info(f"Enhanced generic recommendation query: {enhanced_query}")
        
        # Special enhancement for generic comparison queries (which card gives/earns/offers)
        generic_comp_keywords = ["which card gives", "which card earns", "which card offers", "which card has", "which card provides", "which cards give", "which cards earn", "which cards offer", "which cards have", "what card gives", "what card earns", "what card offers"]
        if any(keyword in query_text.lower() for keyword in generic_comp_keywords) and not card_filter:
            # Add relevant terms for comprehensive comparison
            enhanced_query += " rewards earning rate points miles benefits exclusions"
            logger.info(f"Enhanced generic comparison query: {enhanced_query}")
        
            
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
            
            # For comparison queries, ensure balanced representation from multiple cards
            if not card_filter and "infinia" in query_text.lower() and "atlas" in query_text.lower():
                logger.info("Applying balanced search for comparison query")
                results = self._balance_comparison_results(results, top_k)
            
            # If card_filter is specified, post-process results to filter by card name
            if card_filter and results:
                # Import here to avoid circular import
                from services.query_enhancer import QueryEnhancer
                enhancer = QueryEnhancer()
                
                # Get the actual card name from mapping
                actual_card_name = enhancer.card_name_mapping.get(card_filter, card_filter)
                
                filtered_results = []
                for result in results:
                    card_name = result.get('cardName', '')
                    # Check if this document matches the requested card
                    if (actual_card_name.lower() in card_name.lower() or 
                        card_filter.lower() in card_name.lower() or 
                        any(word in card_name.lower() for word in card_filter.lower().split())):
                        filtered_results.append(result)
                
                logger.info(f"Post-filtered results: {len(filtered_results)}/{len(results)} documents match '{card_filter}' (mapped to '{actual_card_name}')")
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

    def _balance_comparison_results(self, results: List[Dict], top_k: int) -> List[Dict]:
        """Balance search results for comparison queries to ensure fair representation"""
        if not results:
            return results
        
        # Separate results by card
        infinia_docs = []
        atlas_docs = []
        other_docs = []
        
        for result in results:
            card_name = result.get('cardName', '').lower()
            if 'infinia' in card_name:
                infinia_docs.append(result)
            elif 'atlas' in card_name:
                atlas_docs.append(result)
            else:
                other_docs.append(result)
        
        logger.info(f"Before balancing: Infinia={len(infinia_docs)}, Atlas={len(atlas_docs)}, Other={len(other_docs)}")
        
        # For comparison queries, aim for 40% Infinia, 40% Atlas, 20% other
        target_infinia = max(1, int(top_k * 0.4))
        target_atlas = max(1, int(top_k * 0.4)) 
        target_other = max(0, top_k - target_infinia - target_atlas)
        
        # Select balanced results
        balanced_results = []
        balanced_results.extend(infinia_docs[:target_infinia])
        balanced_results.extend(atlas_docs[:target_atlas])
        balanced_results.extend(other_docs[:target_other])
        
        # If we still need more results, fill from remaining docs
        remaining_slots = top_k - len(balanced_results)
        if remaining_slots > 0:
            remaining_docs = infinia_docs[target_infinia:] + atlas_docs[target_atlas:] + other_docs[target_other:]
            balanced_results.extend(remaining_docs[:remaining_slots])
        
        logger.info(f"After balancing: Total={len(balanced_results)}, Target was {top_k}")
        
        # Log the final balance
        final_infinia = sum(1 for r in balanced_results if 'infinia' in r.get('cardName', '').lower())
        final_atlas = sum(1 for r in balanced_results if 'atlas' in r.get('cardName', '').lower())
        final_other = len(balanced_results) - final_infinia - final_atlas
        logger.info(f"Final balance: Infinia={final_infinia}, Atlas={final_atlas}, Other={final_other}")
        
        return balanced_results[:top_k]

    def _fallback_response(self, query: str) -> List[Dict]:
        """Provides a fallback response on API failure."""
        logger.warning(f"Using fallback response for query: {query}")
        return [{
            'content': f"Search is temporarily unavailable for your query: '{query}'. Please check logs.",
            'cardName': "System",
            'section': "Error",
            'similarity': 0.0
        }]