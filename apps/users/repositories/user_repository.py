"""
Repositorio para el modelo User.

Este módulo implementa el patrón Repository para abstraer el acceso
a datos del modelo User, proporcionando una interfaz limpia para las
operaciones de persistencia.
"""

from typing import Protocol
from django.db.models import QuerySet

from apps.users.models import User


class UserRepositoryProtocol(Protocol):
    """
    Interface (Protocol) para el repositorio de usuarios.

    Define el contrato que debe cumplir cualquier implementación
    del repositorio de usuarios.
    """

    def get_by_id(self, user_id: int) -> User | None:
        """Obtiene un usuario por ID."""
        ...

    def get_by_email(self, email: str) -> User | None:
        """Obtiene un usuario por email."""
        ...

    def get_by_username(self, username: str) -> User | None:
        """Obtiene un usuario por username."""
        ...

    def filter_by_tenant(self, tenant_id: str) -> list[User]:
        """Filtra usuarios por tenant."""
        ...

    def create(self, **kwargs) -> User:
        """Crea un nuevo usuario."""
        ...

    def update(self, user: User, **kwargs) -> User:
        """Actualiza un usuario existente."""
        ...

    def delete(self, user: User) -> None:
        """Elimina un usuario."""
        ...

    def all(self) -> QuerySet[User]:
        """Obtiene todos los usuarios."""
        ...


class UserRepository:
    """
    Implementación del repositorio de usuarios.

    Proporciona métodos para realizar operaciones CRUD sobre el
    modelo User, abstrayendo la lógica de acceso a datos.
    """

    def get_by_id(self, user_id: int) -> User | None:
        """
        Obtiene un usuario por su ID.

        Args:
            user_id: ID del usuario a buscar.

        Returns:
            User | None: Usuario si existe, None en caso contrario.
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> User | None:
        """
        Obtiene un usuario por su email.

        Args:
            email: Email del usuario a buscar.

        Returns:
            User | None: Usuario si existe, None en caso contrario.
        """
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> User | None:
        """
        Obtiene un usuario por su username.

        Args:
            username: Username del usuario a buscar.

        Returns:
            User | None: Usuario si existe, None en caso contrario.
        """
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    def filter_by_tenant(self, tenant_id: str) -> list[User]:
        """
        Filtra usuarios que pertenecen a un tenant específico.

        Args:
            tenant_id: ID del tenant.

        Returns:
            list[User]: Lista de usuarios que pertenecen al tenant.

        Note:
            Requiere que la relación con TenantMembership esté
            configurada.
        """
        return list(
            User.objects.filter(
                tenantmembership__tenant_id=tenant_id,
                tenantmembership__is_active=True
            ).distinct()
        )

    def create(self, **kwargs) -> User:
        """
        Crea un nuevo usuario.

        Args:
            **kwargs: Campos del usuario a crear.

        Returns:
            User: Usuario creado.

        Note:
            Para crear usuarios con contraseña, usar
            User.objects.create_user() directamente o llamar
            a set_password() después de la creación.
        """
        return User.objects.create(**kwargs)

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        **extra_fields
    ) -> User:
        """
        Crea un nuevo usuario con contraseña hasheada.

        Args:
            username: Nombre de usuario.
            email: Correo electrónico.
            password: Contraseña en texto plano (será hasheada).
            **extra_fields: Campos adicionales del usuario.

        Returns:
            User: Usuario creado con contraseña hasheada.
        """
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )

    def update(self, user: User, **kwargs) -> User:
        """
        Actualiza un usuario existente.

        Args:
            user: Instancia del usuario a actualizar.
            **kwargs: Campos a actualizar.

        Returns:
            User: Usuario actualizado.

        Note:
            Si se actualiza la contraseña, usar set_password()
            en lugar de asignar directamente.
        """
        for key, value in kwargs.items():
            setattr(user, key, value)
        user.save()
        return user

    def delete(self, user: User) -> None:
        """
        Elimina un usuario.

        Args:
            user: Instancia del usuario a eliminar.

        Note:
            Considera usar soft delete (is_active=False) en lugar
            de eliminación física para mantener integridad
            referencial.
        """
        user.delete()

    def deactivate(self, user: User) -> User:
        """
        Desactiva un usuario (soft delete).

        Args:
            user: Instancia del usuario a desactivar.

        Returns:
            User: Usuario desactivado.
        """
        user.is_active = False
        user.save()
        return user

    def all(self) -> QuerySet[User]:
        """
        Obtiene todos los usuarios.

        Returns:
            QuerySet[User]: QuerySet con todos los usuarios.
        """
        return User.objects.all()

    def filter_active(self) -> QuerySet[User]:
        """
        Obtiene todos los usuarios activos.

        Returns:
            QuerySet[User]: QuerySet con usuarios activos.
        """
        return User.objects.filter(is_active=True)

    def filter_verified(self) -> QuerySet[User]:
        """
        Obtiene todos los usuarios con email verificado.

        Returns:
            QuerySet[User]: QuerySet con usuarios verificados.
        """
        return User.objects.filter(is_email_verified=True)
