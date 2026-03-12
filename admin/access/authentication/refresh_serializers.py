from rest_framework import serializers
from admin.access.authentication.keycloak_auth import keycloak_openid

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get('refresh_token', '').strip()
        # Handle case where user accidentally includes "Bearer " prefix in the JSON body
        if refresh_token.lower().startswith('bearer '):
            refresh_token = refresh_token[7:].strip()

        if not refresh_token:
            raise serializers.ValidationError({"detail": "Refresh token is missing or empty."})

        try:
            # Exchange refresh token for a new set of tokens
            token_data = keycloak_openid.refresh_token(refresh_token)
            
            # Keycloak returns a dict with 'access_token', 'refresh_token', etc.
            if not token_data or 'access_token' not in token_data:
                raise serializers.ValidationError({"detail": "Invalid refresh token or session expired. Please log in again."})
                
            # Return only the requested fields
            return {
                "access_token": token_data.get('access_token'),
                "expires_in": token_data.get('expires_in'),
            }
        except Exception as e:
            error_msg = str(e)
            
            # DIAGNOSTIC: Keep basic decoding for error cases to help debugging
            token_info = "Could not decode token."
            try:
                import jwt
                decoded = jwt.decode(refresh_token, options={"verify_signature": False})
                from datetime import datetime
                exp = datetime.fromtimestamp(decoded.get('exp')).strftime('%Y-%m-%d %H:%M:%S') if decoded.get('exp') else 'N/A'
                token_info = {
                    "client": decoded.get('azp'),
                    "expires_at": exp,
                }
            except Exception:
                pass

            if 'invalid_grant' in error_msg or '400' in error_msg:
                from .keycloak_auth import KEYCLOAK_CLIENT_ID
                raise serializers.ValidationError({
                    "detail": "Keycloak rejected the refresh token. It might be expired or already used.",
                    "debug_info": {
                        "configured_client_id": KEYCLOAK_CLIENT_ID,
                        "token_payload": token_info
                    }
                })
            raise serializers.ValidationError({"detail": f"Token refresh failed: {error_msg}"})
