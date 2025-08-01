"""
Pydantic models for FastAPI request/response schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Request Models
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User's question or message")
    model: str = Field("gemini-1.5-pro", description="AI model to use")
    query_mode: str = Field("General Query", description="Query mode (General Query, Specific Card, Compare Cards)")
    card_filter: Optional[str] = Field(None, description="Card filter for specific card queries")
    top_k: int = Field(10, ge=1, le=15, description="Number of search results to retrieve")

class QueryEnhanceRequest(BaseModel):
    """Request model for query enhancement endpoint"""
    query: str = Field(..., description="Query to enhance")

# Response Models
class DocumentSource(BaseModel):
    """Model for document source information"""
    cardName: str = Field(..., description="Name of the credit card")
    section: str = Field(..., description="Section of the document")
    content: str = Field(..., description="Content of the document")
    similarity: float = Field(0.0, description="Similarity score")

class UsageInfo(BaseModel):
    """Model for usage and cost information"""
    tokens: int = Field(0, description="Number of tokens used")
    cost: float = Field(0.0, description="Cost in USD")
    model: str = Field("", description="Model used")
    input_tokens: Optional[int] = Field(None, description="Input tokens")
    output_tokens: Optional[int] = Field(None, description="Output tokens")
    total_tokens: Optional[int] = Field(None, description="Total tokens")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="AI generated answer")
    sources: List[DocumentSource] = Field([], description="Document sources used")
    embedding_usage: UsageInfo = Field(..., description="Search/embedding usage info")
    llm_usage: UsageInfo = Field(..., description="LLM usage info")
    total_cost: float = Field(0.0, description="Total cost of the query")
    enhanced_question: str = Field("", description="Enhanced version of the question")
    metadata: Dict[str, Any] = Field({}, description="Additional metadata")

class QueryEnhanceResponse(BaseModel):
    """Response model for query enhancement endpoint"""
    enhanced_query: str = Field(..., description="Enhanced query")
    metadata: Dict[str, Any] = Field({}, description="Query metadata")

class ModelInfo(BaseModel):
    """Model information"""
    name: str = Field(..., description="Model name")
    provider: str = Field(..., description="Provider (OpenAI, Google)")
    cost_per_1k_input: float = Field(..., description="Cost per 1K input tokens")
    cost_per_1k_output: float = Field(..., description="Cost per 1K output tokens")
    available: bool = Field(True, description="Whether model is available")
    description: str = Field("", description="Model description")

class ConfigResponse(BaseModel):
    """Response model for configuration endpoint"""
    available_models: List[ModelInfo] = Field([], description="Available AI models")
    supported_cards: List[str] = Field([], description="Supported credit cards")
    default_model: str = Field("gemini-1.5-pro", description="Default AI model")
    max_top_k: int = Field(15, description="Maximum number of search results")

class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field("healthy", description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    services: Dict[str, bool] = Field({}, description="Service availability")
    version: str = Field("1.0.0", description="API version")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Timestamp")

# Streaming Models
class StreamChunk(BaseModel):
    """Model for streaming chunk data"""
    type: str = Field(..., description="Chunk type: 'chunk', 'complete', 'error', 'status'")
    content: Optional[str] = Field(None, description="Text content for chunk type")
    sources: Optional[List[DocumentSource]] = Field(None, description="Sources for complete type")
    embedding_usage: Optional[UsageInfo] = Field(None, description="Embedding usage for complete type")
    llm_usage: Optional[UsageInfo] = Field(None, description="LLM usage for complete type") 
    total_cost: Optional[float] = Field(None, description="Total cost for complete type")
    enhanced_question: Optional[str] = Field(None, description="Enhanced question for complete type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata for complete type")

class ChatStreamRequest(BaseModel):
    """Request model for streaming chat endpoint"""
    message: str = Field(..., description="User's question or message")
    model: str = Field("gemini-1.5-pro", description="AI model to use")
    query_mode: str = Field("General Query", description="Query mode (General Query, Specific Card, Compare Cards)")
    card_filter: Optional[str] = Field(None, description="Card filter for specific card queries")
    top_k: int = Field(10, ge=1, le=15, description="Number of search results to retrieve")

# Authentication Models
class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication"""
    token: str = Field(..., description="Google OAuth token")

class AuthResponse(BaseModel):
    """Response model for authentication"""
    success: bool = Field(..., description="Authentication success")
    jwt_token: Optional[str] = Field(None, description="JWT token for authenticated sessions")
    user: Optional[Dict[str, Any]] = Field(None, description="User information")
    message: str = Field("", description="Response message")

class UserStatsResponse(BaseModel):
    """Response model for user statistics"""
    user: Dict[str, Any] = Field(..., description="User information")
    stats: Dict[str, Any] = Field(..., description="User statistics")

class QueryLimitResponse(BaseModel):
    """Response model for query limit check"""
    can_query: bool = Field(..., description="Whether user can make a query")
    current_count: int = Field(..., description="Current daily query count")
    limit: int = Field(..., description="Daily query limit (-1 for unlimited)")
    remaining: Optional[int] = Field(None, description="Remaining queries (None for unlimited)")