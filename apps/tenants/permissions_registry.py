"""
Registro central de permisos granulares disponibles.

Este archivo define la lista maestra de permisos que pueden ser asignados
a los miembros de un tenant. El frontend puede consumnir esta lista
para generar la UI de gestión de equipo.
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PermissionDefinition:
    codename: str
    name: str
    description: str


# Estructura de permisos agrupados por Módulo
AVAILABLE_PERMISSIONS: Dict[str, List[PermissionDefinition]] = {
    "recruitment": [
        PermissionDefinition(
            codename="recruitment.manage_vacancies",
            name="Gestionar Vacantes",
            description="Crear, editar, publicar y cerrar vacantes.",
        ),
        PermissionDefinition(
            codename="recruitment.view_candidates",
            name="Ver Candidatos",
            description="Ver lista de personas que han postulado.",
        ),
        PermissionDefinition(
            codename="recruitment.manage_candidates",
            name="Gestionar Candidatos",
            description=(
                "Mover candidatos de etapa, rechazarlos o contratarlos."
            ),
        ),
    ],
    "team": [
        PermissionDefinition(
            codename="team.invite_members",
            name="Invitar Miembros",
            description="Enviar invitaciones a nuevos usuarios.",
        ),
        PermissionDefinition(
            codename="team.manage_roles",
            name="Gestionar Roles",
            description="Asignar o revocar permisos a otros miembros.",
        ),
    ],
}


def get_all_permissions_list() -> List[Dict]:
    """Retorna la lista plana de permisos para API."""
    flat_list = []
    for category, perms in AVAILABLE_PERMISSIONS.items():
        for p in perms:
            flat_list.append(
                {
                    "category": category,
                    "codename": p.codename,
                    "name": p.name,
                    "description": p.description,
                }
            )
    return flat_list
