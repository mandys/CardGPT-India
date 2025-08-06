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
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences for personalization")
    session_id: Optional[str] = Field(None, description="Session ID for preference tracking")

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

# User Preference Models
class UserPreferences(BaseModel):
    """Model for user preferences"""
    travel_type: Optional[str] = Field(None, description="Travel preference: domestic | international | both")
    lounge_access: Optional[str] = Field(None, description="Lounge access needs: solo | with_guests | family")
    fee_willingness: Optional[str] = Field(None, description="Annual fee comfort: 0-1000 | 1000-5000 | 5000-10000 | 10000+")
    current_cards: Optional[List[str]] = Field(None, description="List of current credit cards")
    preferred_banks: Optional[List[str]] = Field(None, description="List of preferred banks")
    spend_categories: Optional[List[str]] = Field(None, description="Top spending categories")

class UserPreferenceRequest(BaseModel):
    """Request model for creating/updating user preferences"""
    preferences: UserPreferences = Field(..., description="User preferences to update")
    session_id: Optional[str] = Field(None, description="Session ID for anonymous users")

class UserPreferenceResponse(BaseModel):
    """Response model for user preferences"""
    user_id: str = Field(..., description="User ID or session ID")
    preferences: UserPreferences = Field(..., description="User preferences")
    completion_status: Dict[str, bool] = Field({}, description="Preference completion status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

class PreferenceAnalytics(BaseModel):
    """Model for preference analytics data"""
    most_common_travel_type: str = Field("", description="Most common travel preference")
    average_fee_willingness: str = Field("", description="Average fee willingness")
    popular_banks: List[str] = Field([], description="Most popular banks")
    completion_rate: float = Field(0.0, description="Preference completion rate")

# Enhanced Chat Request with User Preferences
class EnhancedChatRequest(BaseModel):
    """Enhanced chat request with user preferences"""
    message: str = Field(..., description="User's question or message")
    model: str = Field("gemini-1.5-pro", description="AI model to use")
    query_mode: str = Field("General Query", description="Query mode")
    card_filter: Optional[str] = Field(None, description="Card filter for specific card queries")
    top_k: int = Field(10, ge=1, le=15, description="Number of search results to retrieve")
    user_preferences: Optional[UserPreferences] = Field(None, description="User preferences for personalization")
    session_id: Optional[str] = Field(None, description="Session ID for anonymous users")

class AmbiguityDetectionResponse(BaseModel):
    """Response model for query ambiguity detection"""
    is_ambiguous: bool = Field(..., description="Whether the query is ambiguous")
    missing_context: List[str] = Field([], description="List of missing context types")
    suggested_questions: List[str] = Field([], description="Suggested clarification questions")
    refinement_buttons: List[Dict[str, str]] = Field([], description="Quick refinement button options")