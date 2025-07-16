"""
Vertex AI Search Configuration
Provides configuration management for Google Cloud Vertex AI Search integration
"""

import os
from typing import Dict, Any, Optional

class VertexConfig:
    """Configuration manager for Vertex AI Search settings"""
    
    def __init__(self):
        self.project_id = None
        self.location = None
        self.data_store_id = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from environment variables or Streamlit secrets"""
        # Try to load from environment variables first
        self.project_id = os.getenv("GCP_PROJECT_ID")
        self.location = os.getenv("GCP_LOCATION", "global")
        self.data_store_id = os.getenv("GCP_DATA_STORE_ID")
        
        # If running in Streamlit, try to load from secrets
        try:
            import streamlit as st
            if hasattr(st, 'secrets'):
                self.project_id = self.project_id or st.secrets.get("GCP_PROJECT_ID")
                self.location = self.location or st.secrets.get("GCP_LOCATION", "global")
                self.data_store_id = self.data_store_id or st.secrets.get("GCP_DATA_STORE_ID")
        except ImportError:
            pass
    
    def is_configured(self) -> bool:
        """Check if Vertex AI Search is properly configured"""
        return bool(self.project_id and self.data_store_id)
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return {
            "project_id": self.project_id,
            "location": self.location,
            "data_store_id": self.data_store_id,
            "is_configured": self.is_configured()
        }
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the configuration and return status"""
        issues = []
        
        if not self.project_id:
            issues.append("GCP_PROJECT_ID is not set")
        
        if not self.data_store_id:
            issues.append("GCP_DATA_STORE_ID is not set")
        
        if not self.location:
            issues.append("GCP_LOCATION is not set (defaulting to 'global')")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": self.get_config()
        }
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for Vertex AI Search"""
        return """
        🚀 Vertex AI Search Setup Instructions:
        
        1. Set up Google Cloud Project:
           - Create a Google Cloud Project or use an existing one
           - Enable the Vertex AI Search API
           - Set up authentication (gcloud auth application-default login)
        
        2. Create Vertex AI Search Data Store:
           - Go to Vertex AI > Search and Conversation
           - Create a new Search App
           - Create a Data Store and upload your JSON files
           - Note down the Data Store ID
        
        3. Configure Environment Variables:
           - Set GCP_PROJECT_ID to your Google Cloud Project ID
           - Set GCP_DATA_STORE_ID to your Vertex AI Search Data Store ID
           - Set GCP_LOCATION to your preferred region (default: global)
        
        4. Or use Streamlit secrets:
           - Create .streamlit/secrets.toml file
           - Add the configuration values as shown in the example
        
        For your reference:
        - Data Store ID from screenshot: cardgpt-engine_1752662874226
        - Location: global (as shown in screenshot)
        """

# Global configuration instance
vertex_config = VertexConfig()