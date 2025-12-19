"""
Vistas para gestión de permisos.
"""
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.permissions import IsTenantAdmin
from apps.tenants.permissions_registry import get_all_permissions_list


class PermissionListView(APIView):
    """
    Lista todos los permisos granulares disponibles en el sistema.

    Endpoint protegido: Solo accesible por Tenant Admins.
    """

    permission_classes = [IsAuthenticated, IsTenantAdmin]

    def get(self, request):
        """
        Retorna la lista de permisos disponibles.

        Returns:
            List[Dict]: Lista de objetos de permiso.
        """
        permissions = get_all_permissions_list()
        return Response(permissions)
