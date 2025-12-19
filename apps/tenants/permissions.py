from rest_framework.permissions import BasePermission

from apps.tenants.models import TenantMembership, TenantRole


class IsTenantMember(BasePermission):
    """
    Permite acceso a usuarios que son miembros activos del tenant actual.
    """

    def has_permission(self, request, view):
        # Primero validamos autenticación básica
        if not request.user or not request.user.is_authenticated:
            return False

        # El tenant_id debe haber sido inyectado por TenantMiddleware
        if not hasattr(request, "tenant_id") or not request.tenant_id:
            return False

        # Verificar membresía activa
        return TenantMembership.objects.filter(
            user=request.user, tenant_id=request.tenant_id, is_active=True
        ).exists()


class IsTenantAdmin(BasePermission):
    """
    Permite acceso solo a Dueños y Administradores del tenant.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request, "tenant_id") or not request.tenant_id:
            return False

        membership = (
            TenantMembership.objects.filter(
                user=request.user, tenant_id=request.tenant_id, is_active=True
            )
            .select_related("tenant")
            .first()
        )

        if not membership:
            return False

        return membership.role in [TenantRole.OWNER, TenantRole.ADMIN]


class IsTenantOwner(BasePermission):
    """
    Permite acceso solo al Dueño del tenant.
    """

    def has_permission(self, request, view):
        print(request.user)
        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request, "tenant_id") or not request.tenant_id:
            return False

        membership = TenantMembership.objects.filter(
            user=request.user, tenant_id=request.tenant_id, is_active=True
        ).first()

        if not membership:
            return False

        return membership.role == TenantRole.OWNER


class HasTenantPermission:
    """
    Permiso granular dinámico.
    Permite acceso si:
    1. El usuario es Dueño o Admin (Superpoderes).
    2. El usuario tiene el permiso explícito en su lista de permisos.

    Uso: permission_classes = [
        HasTenantPermission('recruitment.create_vacancy')
    ]
    """

    def __init__(self, required_perm: str):
        self.required_perm = required_perm

    def __call__(self):
        return self

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if not hasattr(request, "tenant_id") or not request.tenant_id:
            return False

        membership = TenantMembership.objects.filter(
            user=request.user, tenant_id=request.tenant_id, is_active=True
        ).first()

        if not membership:
            return False

        # 1. Superusers del tenant tienen acceso total
        if membership.role in [TenantRole.OWNER, TenantRole.ADMIN]:
            return True

        # 2. Verificar permiso explícito simple (string match)
        # El campo permissions es un JSON list: ["app.action", "other.action"]
        return self.required_perm in membership.permissions
