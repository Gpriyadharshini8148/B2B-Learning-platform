from drf_spectacular.extensions import OpenApiAuthenticationExtension
from .keycloak_auth import KeycloakAuthentication
from rest_framework.authentication import SessionAuthentication

class KeycloakAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = KeycloakAuthentication
    name = 'KeycloakAuthentication'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }

class SessionAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = SessionAuthentication
    name = 'SessionAuthentication'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'sessionid', 
        }
