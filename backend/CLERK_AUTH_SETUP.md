# Clerk Authentication Setup Guide

## Overview

This project now uses proper Clerk JWT authentication for user preferences and authenticated endpoints.

## Environment Variables Required

### Backend (.env)
```bash
# Clerk Authentication Keys
CLERK_SECRET_KEY="sk_test_your-clerk-secret-key-here"
REACT_APP_CLERK_PUBLISHABLE_KEY="pk_test_your-clerk-publishable-key-here"

# Other existing variables...
GEMINI_API_KEY="your-gemini-key-here"
# ... etc
```

### Frontend (.env.local)
```bash
# Clerk Frontend Integration
REACT_APP_CLERK_PUBLISHABLE_KEY="pk_test_your-clerk-publishable-key-here"
REACT_APP_API_URL="https://cardgpt-india-production.up.railway.app"
```

## Implementation Details

### Backend Authentication Flow

1. **ClerkAuthService** (`services/clerk_auth.py`)
   - Validates JWT tokens from Clerk
   - Extracts user ID from token payload
   - Handles authentication errors gracefully

2. **Preferences API** (`api/preferences.py`)
   - Uses `get_clerk_user_id()` dependency for authentication
   - Extracts user ID from Authorization header
   - Supports both authenticated and session-based preferences

3. **Token Validation**
   - Development: Simplified JWT decoding for testing
   - Production: Should implement full JWKS endpoint validation

### Frontend Integration

1. **API Client** (`cardgpt-ui/src/services/api.ts`)
   - Updated to accept optional `clerkToken` parameter
   - Maintains backward compatibility with localStorage tokens
   - Supports both authenticated and anonymous users

2. **Clerk Integration**
   - Already integrated via `@clerk/clerk-react`
   - ClerkProvider wraps entire app in `index.tsx`

## Usage Examples

### Frontend: Using Clerk Token with Preferences

```typescript
import { useAuth } from '@clerk/clerk-react';
import { apiClient } from '../services/api';

function MyComponent() {
  const { getToken } = useAuth();

  const handleSavePreferences = async (preferences: UserPreferences) => {
    try {
      const token = await getToken();
      await apiClient.updateUserPreferences(preferences, token);
    } catch (error) {
      console.error('Failed to save preferences:', error);
    }
  };
}
```

### Backend: Protected Endpoint

```python
from fastapi import Depends
from api.preferences import get_clerk_user_id

@router.get("/protected-endpoint")
async def protected_route(user_id: str = Depends(get_clerk_user_id)):
    return {"message": f"Hello user {user_id}"}
```

## Testing

### Development Testing
```bash
# Test authentication service
python backend/test_clerk_auth.py

# Test API endpoints (requires actual Clerk tokens)
curl -X GET http://localhost:8000/api/preferences \
  -H "Authorization: Bearer your-clerk-jwt-token"
```

### Production Testing
1. Sign up/sign in through Clerk UI
2. Get JWT token from browser dev tools or `await getToken()`
3. Test preferences endpoints with real tokens

## Security Notes

### Development vs Production

**Development (Current)**:
- Simplified JWT decoding without signature verification
- Logs token payloads for debugging
- Uses unverified token extraction

**Production (TODO)**:
- Full JWKS endpoint integration
- Proper signature verification
- Token expiration checking
- Rate limiting and abuse protection

### Token Security
- Tokens should be short-lived (1 hour typical)
- Never log tokens in production
- Use HTTPS only for token transmission
- Implement proper CORS policies

## Troubleshooting

### Common Issues

1. **"Authentication required" errors**
   - Check that CLERK_SECRET_KEY is set in backend
   - Verify REACT_APP_CLERK_PUBLISHABLE_KEY is set in frontend
   - Ensure Clerk tokens are being passed correctly

2. **"Token missing required field" errors**
   - Clerk token format may have changed
   - Check token payload structure in logs
   - Verify token is valid and not expired

3. **"Authentication verification failed" errors**
   - Check backend logs for specific error details
   - Verify token format (should start with "Bearer ")
   - Ensure Clerk service is properly configured

### Debug Commands

```bash
# Check if Clerk auth service is working
python -c "from services.clerk_auth import clerk_auth; print(f'Enabled: {clerk_auth.enabled}')"

# Test preferences API import
python -c "from api.preferences import get_clerk_user_id; print('✅ Auth function available')"

# Check environment variables
echo "Clerk Secret: ${CLERK_SECRET_KEY:0:20}..."
echo "Clerk Publishable: ${REACT_APP_CLERK_PUBLISHABLE_KEY:0:20}..."
```

## Migration Path

### From Old JWT System
1. ✅ Install PyJWT and cryptography dependencies
2. ✅ Create ClerkAuthService with proper JWT validation
3. ✅ Update preferences API to use Clerk authentication
4. ✅ Update frontend API client to support Clerk tokens
5. 🔲 Update frontend components to use `getToken()` from Clerk
6. 🔲 Remove legacy JWT token handling
7. 🔲 Implement production JWKS endpoint integration

### Next Steps
1. **Frontend Components**: Update React components to use Clerk's `getToken()` method
2. **Production Security**: Implement full JWKS endpoint validation
3. **Error Handling**: Add better error handling and user feedback
4. **Testing**: Add comprehensive authentication tests
5. **Documentation**: Update API documentation with authentication requirements

## Support

For Clerk-specific issues:
- [Clerk Documentation](https://clerk.com/docs)
- [Clerk JWT Guide](https://clerk.com/docs/backend-requests/handling/manual-jwt)
- [Clerk React Integration](https://clerk.com/docs/quickstarts/react)

For this implementation:
- Check backend logs for authentication errors
- Use test script: `python backend/test_clerk_auth.py`
- Verify environment variables are properly set