"""
Servicios de aplicación para el modelo User.

Este módulo contiene los casos de uso relacionados con usuarios,
implementando la lógica de negocio y orquestando las operaciones
a través de repositorios.
"""

from typing import Any
from django.db import transaction

from apps.users.models import User
from apps.users.repositories import UserRepository


class UserService:
    """
    Servicio de aplicación para gestión de usuarios.

    Implementa los casos de uso relacionados con usuarios,
    orquestando la lógica de negocio y delegando la persistencia
    al repositorio.

    Attributes:
        repository: Repositorio de usuarios para acceso a datos.
    """

    def __init__(self, repository: UserRepository | None = None):
        """
        Inicializa el servicio con el repositorio.

        Args:
            repository: Repositorio de usuarios. Si no se
                proporciona, se crea una instancia por defecto.
        """
        self.repository = repository or UserRepository()

    @transaction.atomic
    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        phone: str | None = None,
        **extra_fields: Any
    ) -> User:
        """
        Registra un nuevo usuario en el sistema.

        Args:
            username: Nombre de usuario único.
            email: Correo electrónico único.
            password: Contraseña en texto plano.
            first_name: Nombre del usuario.
            last_name: Apellido del usuario.
            phone: Número de teléfono (opcional).
            **extra_fields: Campos adicionales.

        Returns:
            User: Usuario creado.

        Raises:
            ValueError: Si el username o email ya existen.
        """
        # Validar que el username no exista
        if self.repository.get_by_username(username):
            raise ValueError(
                f"El username '{username}' ya está en uso."
            )

        # Validar que el email no exista
        if self.repository.get_by_email(email):
            raise ValueError(
                f"El email '{email}' ya está registrado."
            )

        # Crear el usuario
        user = self.repository.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            **extra_fields
        )

        return user

    @transaction.atomic
    def update_profile(
        self,
        user_id: int,
        **profile_data: Any
    ) -> User | None:
        """
        Actualiza el perfil de un usuario.

        Args:
            user_id: ID del usuario a actualizar.
            **profile_data: Datos del perfil a actualizar.

        Returns:
            User | None: Usuario actualizado o None si no existe.

        Raises:
            ValueError: Si se intenta actualizar campos no
                permitidos.

        Note:
            No permite actualizar username, email o password
            directamente. Usar métodos específicos para eso.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        # Campos que no se pueden actualizar por este método
        forbidden_fields = {
            'username', 'email', 'password',
            'is_staff', 'is_superuser', 'is_active'
        }

        # Validar que no se intenten actualizar campos prohibidos
        if any(field in profile_data for field in forbidden_fields):
            raise ValueError(
                f"No se pueden actualizar los campos: "
                f"{forbidden_fields & profile_data.keys()}"
            )

        # Actualizar el usuario
        return self.repository.update(user, **profile_data)

    @transaction.atomic
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> User | None:
        """
        Cambia la contraseña de un usuario.

        Args:
            user_id: ID del usuario.
            old_password: Contraseña actual.
            new_password: Nueva contraseña.

        Returns:
            User | None: Usuario actualizado o None si no existe.

        Raises:
            ValueError: Si la contraseña actual es incorrecta.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        # Verificar la contraseña actual
        if not user.check_password(old_password):
            raise ValueError("La contraseña actual es incorrecta.")

        # Cambiar la contraseña
        user.set_password(new_password)
        user.save()

        return user

    @transaction.atomic
    def update_email(
        self,
        user_id: int,
        new_email: str
    ) -> User | None:
        """
        Actualiza el email de un usuario.

        Args:
            user_id: ID del usuario.
            new_email: Nuevo correo electrónico.

        Returns:
            User | None: Usuario actualizado o None si no existe.

        Raises:
            ValueError: Si el nuevo email ya está en uso.

        Note:
            Al cambiar el email, se marca como no verificado.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        # Validar que el nuevo email no esté en uso
        existing_user = self.repository.get_by_email(new_email)
        if existing_user and existing_user.id != user_id:
            raise ValueError(
                f"El email '{new_email}' ya está en uso."
            )

        # Actualizar email y marcar como no verificado
        user.email = new_email
        user.is_email_verified = False
        user.save()

        return user

    @transaction.atomic
    def verify_email(self, user_id: int) -> User | None:
        """
        Marca el email de un usuario como verificado.

        Args:
            user_id: ID del usuario.

        Returns:
            User | None: Usuario actualizado o None si no existe.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        user.is_email_verified = True
        user.save()

        return user

    @transaction.atomic
    def deactivate_user(self, user_id: int) -> User | None:
        """
        Desactiva un usuario (soft delete).

        Args:
            user_id: ID del usuario a desactivar.

        Returns:
            User | None: Usuario desactivado o None si no existe.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        return self.repository.deactivate(user)

    @transaction.atomic
    def activate_user(self, user_id: int) -> User | None:
        """
        Activa un usuario previamente desactivado.

        Args:
            user_id: ID del usuario a activar.

        Returns:
            User | None: Usuario activado o None si no existe.
        """
        user = self.repository.get_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        user.save()

        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Obtiene un usuario por ID.

        Args:
            user_id: ID del usuario.

        Returns:
            User | None: Usuario si existe, None en caso contrario.
        """
        return self.repository.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """
        Obtiene un usuario por email.

        Args:
            email: Email del usuario.

        Returns:
            User | None: Usuario si existe, None en caso contrario.
        """
        return self.repository.get_by_email(email)

    def get_users_by_tenant(self, tenant_id: str) -> list[User]:
        """
        Obtiene todos los usuarios de un tenant.

        Args:
            tenant_id: ID del tenant.

        Returns:
            list[User]: Lista de usuarios del tenant.
        """
        return self.repository.filter_by_tenant(tenant_id)
