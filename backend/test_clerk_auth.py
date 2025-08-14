#!/usr/bin/env python3
"""
Test script for Clerk authentication service
Tests JWT token validation without requiring actual Clerk setup
"""

import os
import jwt
from datetime import datetime, timedelta
from services.clerk_auth import ClerkAuthService

def test_clerk_auth():
    """Test Clerk authentication service with mock tokens"""
    print("🧪 Testing Clerk Authentication Service")
    print("=" * 50)
    
    # Test 1: Service initialization without keys
    print("\n1️⃣ Testing service initialization (no keys):")
    service = ClerkAuthService()
    print(f"   Service enabled: {service.enabled}")
    
    # Test 2: Set up mock Clerk environment
    print("\n2️⃣ Testing with mock Clerk keys:")
    os.environ['REACT_APP_CLERK_PUBLISHABLE_KEY'] = 'pk_test_mock'
    os.environ['CLERK_SECRET_KEY'] = 'sk_test_mock_secret_key'
    
    service_with_keys = ClerkAuthService()
    print(f"   Service enabled: {service_with_keys.enabled}")
    
    # Test 3: Create a mock JWT token (similar to what Clerk would issue)
    print("\n3️⃣ Testing JWT token validation:")
    
    # Create a mock token payload (similar to Clerk's format)
    mock_payload = {
        'sub': 'user_2Abc123def456',  # Clerk user ID format
        'iss': 'https://clerk.example.com',  # Clerk issuer
        'iat': int(datetime.utcnow().timestamp()),
        'exp': int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        'aud': 'test-audience'
    }
    
    # Create token without signature verification (for development testing)
    mock_token = jwt.encode(mock_payload, 'mock-secret', algorithm='HS256')
    print(f"   Mock token created: {mock_token[:30]}...")
    
    try:
        # Test token verification (will use unverified decoding in development)
        result = service_with_keys.verify_clerk_token(mock_token)
        print(f"✅ Token verified successfully!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Token payload keys: {list(result['token_payload'].keys())}")
        
        # Test user ID extraction
        user_id = service_with_keys.extract_user_id_from_request(f"Bearer {mock_token}")
        print(f"✅ User ID extraction: {user_id}")
        
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
    
    # Test 4: Test invalid tokens
    print("\n4️⃣ Testing error handling:")
    
    try:
        service_with_keys.verify_clerk_token("invalid-token")
    except Exception as e:
        print(f"✅ Invalid token correctly rejected: {type(e).__name__}")
    
    try:
        service_with_keys.extract_user_id_from_request("invalid-auth")
    except Exception as e:
        print(f"✅ Invalid auth header correctly rejected: {type(e).__name__}")
    
    try:
        service_with_keys.extract_user_id_from_request(None)
    except Exception as e:
        print(f"✅ Missing auth header correctly rejected: {type(e).__name__}")
    
    print("\n✅ All Clerk authentication tests completed!")
    print("\nℹ️  Note: In production, you should:")
    print("   - Fetch public keys from Clerk's JWKS endpoint")
    print("   - Implement proper signature verification") 
    print("   - Add token expiration checking")
    print("   - Use proper Clerk environment variables")

if __name__ == "__main__":
    test_clerk_auth()