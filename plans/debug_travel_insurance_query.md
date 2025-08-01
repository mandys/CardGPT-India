# Debugging Plan: Travel Insurance Comparison Query

## 1. Issue Description

When a user asks a comparative question like, "Which card offers better travel insurance coverage?", the system returns results for only one card (Axis Atlas) instead of comparing all relevant cards. The response incorrectly states that information for other cards is not available.

## 2. Analysis

The debugging process points to an issue in the query enhancement pipeline.

1.  **`backend/api/chat_stream.py`**: This is the entry point. It correctly calls the `QueryEnhancer` service to enhance the user's query.
2.  **`backend/services/query_enhancer.py`**: This service correctly identifies the query as a generic comparison about "travel insurance" and adds a detailed, specific prompt to the query, instructing the LLM to analyze all cards.
3.  **`backend/services/vertex_retriever.py`**: This service receives the already-enhanced query. However, it contains additional, more generic enhancement logic that is also triggered. This adds broad keywords to the already specific query.

The root cause is the **redundant and conflicting query enhancements** in `vertex_retriever.py`. The generic keywords dilute the specific instructions from `query_enhancer.py`, leading to poor search results from Vertex AI.

## 3. Proposed Solution

To fix this, I will refactor `backend/services/vertex_retriever.py` to remove the legacy query enhancement logic. This will establish `query_enhancer.py` as the single source of truth for query modifications.

The `vertex_retriever.py` will then be responsible only for:
*   Executing the search with the query it receives.
*   Applying the `card_filter` if provided.
*   Processing the response from Vertex AI.

This change will ensure that the carefully crafted prompts from the `QueryEnhancer` are sent to Vertex AI without any modifications that could dilute their specificity.
