"""Repositorios de la app tenants."""

from .tenant_repository import (
    TenantRepository,
    TenantRepositoryProtocol,
)
from .tenant_membership_repository import (
    TenantMembershipRepository,
    TenantMembershipRepositoryProtocol,
)

__all__ = [
    "TenantRepository",
    "TenantRepositoryProtocol",
    "TenantMembershipRepository",
    "TenantMembershipRepositoryProtocol",
]
