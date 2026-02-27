from django.db import models
from .organization import Organization
from admin.access.models.base import BaseModel

class OrganizationSSO(BaseModel):
    PROVIDERS = [
        ("saml", "SAML"),
        ("oauth", "OAuth"),
        ("azure_ad", "Azure AD"),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="sso_configs"
    )
    provider = models.CharField(max_length=50, choices=PROVIDERS)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    metadata_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.organization.name} - {self.provider}"