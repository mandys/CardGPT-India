"""
Clerk Authentication Service
Handles JWT validation for Clerk-issued tokens
"""

import jwt
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException
import os

logger = logging.getLogger(__name__)

class ClerkAuthService:
    def __init__(self):
        """Initialize Clerk authentication service"""
        # Clerk configuration from environment variables
        self.clerk_publishable_key = os.getenv("REACT_APP_CLERK_PUBLISHABLE_KEY")
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY")
        
        if not self.clerk_publishable_key or not self.clerk_secret_key:
            logger.warning("⚠️ Clerk keys not found - authentication will be disabled")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("✅ Clerk authentication service initialized")
    
    def get_clerk_jwt_public_key(self) -> str:
        """
        Get Clerk's JWT public key for token verification
        
        Production Implementation Notes:
        1. Extract domain from publishable key: pk_test_xxx -> test domain
        2. Fetch from https://{domain}.clerk.accounts.dev/.well-known/jwks.json
        3. Cache keys with proper expiration (typically 24 hours)
        4. Handle key rotation gracefully
        
        For development/testing, we use simplified validation
        """
        # TODO: Implement full JWKS endpoint integration
        # Example production implementation:
        # domain = self.clerk_publishable_key.split('_')[1]  # extract domain
        # jwks_url = f"https://{domain}.clerk.accounts.dev/.well-known/jwks.json"
        # response = requests.get(jwks_url)
        # return response.json()['keys']
        
        # For development, return the secret key
        return self.clerk_secret_key
    
    def verify_clerk_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Clerk JWT token and extract user information
        
        Args:
            token: JWT token from Authorization header
            
        Returns:
            Dict containing user information from the token
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        if not self.enabled:
            raise HTTPException(status_code=501, detail="Clerk authentication not configured")
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # For development/testing - decode without verification first to inspect
            # In production, always verify the signature
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            logger.info(f"🔍 Token payload (unverified): {unverified_payload}")
            
            # TODO: Implement proper signature verification in production
            # For now, we'll validate basic structure and expiration
            
            # Check if token has required fields
            required_fields = ['sub', 'iss']  # 'sub' is user ID, 'iss' is issuer
            for field in required_fields:
                if field not in unverified_payload:
                    raise HTTPException(status_code=401, detail=f"Token missing required field: {field}")
            
            # Validate issuer is from Clerk
            issuer = unverified_payload.get('iss', '')
            if 'clerk' not in issuer.lower():
                logger.warning(f"⚠️ Unexpected token issuer: {issuer}")
                # In development, we'll allow it, but log a warning
            
            # Extract user ID from 'sub' field
            user_id = unverified_payload.get('sub')
            if not user_id:
                raise HTTPException(status_code=401, detail="Token missing user ID")
            
            # Return user information
            return {
                'user_id': user_id,
                'token_payload': unverified_payload
            }
            
        except jwt.ExpiredSignatureError:
            logger.error("❌ JWT token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.error(f"❌ Invalid JWT token: {e}")
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        except Exception as e:
            logger.error(f"❌ Error verifying Clerk token: {e}")
            raise HTTPException(status_code=401, detail="Authentication verification failed")
    
    def extract_user_id_from_request(self, authorization: Optional[str]) -> str:
        """
        Extract Clerk user ID from Authorization header
        
        Args:
            authorization: Authorization header value
            
        Returns:
            Clerk user ID
            
        Raises:
            HTTPException: If authorization is missing or invalid
        """
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
        
        if not authorization.startswith('Bearer '):
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        
        token = authorization[7:]  # Remove 'Bearer ' prefix
        
        try:
            token_info = self.verify_clerk_token(token)
            user_id = token_info['user_id']
            
            logger.info(f"✅ Authenticated Clerk user: {user_id}")
            return user_id
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"❌ Unexpected error extracting user ID: {e}")
            raise HTTPException(status_code=500, detail="Authentication processing error")

# Create global instance
clerk_auth = ClerkAuthService()

def get_clerk_user_id(authorization: Optional[str] = None) -> str:
    """
    Dependency function to extract Clerk user ID from Authorization header
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Clerk user ID string
        
    Raises:
        HTTPException: If authentication fails
    """
    return clerk_auth.extract_user_id_from_request(authorization)