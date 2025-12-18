"""
Servicios de aplicación para el modelo User.

Este módulo contiene los casos de uso relacionados con usuarios,
implementando la lógica de negocio y orquestando las operaciones
a través de repositorios.
"""

from typing import Any

from django.db import transaction

from apps.users.models import User
from apps.users.repositories import UserRepository, UserRepositoryProtocol


class UserService:
    """
    Servicio de aplicación para gestión de usuarios.

    Implementa los casos de uso relacionados con usuarios,
    orquestando la lógica de negocio y delegando la persistencia
    al repositorio.

    Attributes:
        repository: Repositorio de usuarios para acceso a datos.
    """

    def __init__(self, repository: UserRepositoryProtocol | None = None):
        """
        Inicializa el servicio con el repositorio.

        Args:
            repository: Implementación del repositorio de usuarios.
                Por defecto usa UserRepository (Django ORM).
                Puede ser cualquier implementación que cumpla
                el contrato UserRepositoryProtocol.
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
        **extra_fields: Any,
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
            raise ValueError(f"El username '{username}' ya está en uso.")

        # Validar que el email no exista
        if self.repository.get_by_email(email):
            raise ValueError(f"El email '{email}' ya está registrado.")

        # Crear el usuario
        user = self.repository.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            **extra_fields,
        )

        return user

    @transaction.atomic
    def update_profile(self, user_id: int, **profile_data: Any) -> User | None:
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
            "username",
            "email",
            "password",
            "is_staff",
            "is_superuser",
            "is_active",
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
        self, user_id: int, old_password: str, new_password: str
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
    def update_email(self, user_id: int, new_email: str) -> User | None:
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
            raise ValueError(f"El email '{new_email}' ya está en uso.")

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

    @transaction.atomic
    def invite_user(
        self,
        tenant_id: str,
        email: str,
        role: str,
        invited_by: User,
        first_name: str = "",
        last_name: str = "",
    ) -> dict:
        """
        Invita a un usuario a un tenant.

        Si el usuario no existe, lo crea.
        Si ya existe, solo lo agrega al tenant.

        Args:
            tenant_id: ID del tenant al que se invita.
            email: Email del usuario invitado.
            role: Rol que tendrá en el tenant.
            invited_by: Usuario que envía la invitación.
            first_name: Nombre del invitado (opcional).
            last_name: Apellido del invitado (opcional).

        Returns:
            dict: Diccionario con 'user', 'created' y 'membership'.
        """
        from django.utils.crypto import get_random_string

        from apps.tenants.models import Tenant, TenantMembership

        # Verificar que el tenant exista
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            raise ValueError("El tenant especificado no existe.")

        # Verificar límites del plan
        if not tenant.can_add_member():
            raise ValueError(
                "Se ha alcanzado el límite de usuarios para este plan."
            )

        # Buscar usuario o crear uno nuevo
        user = self.repository.get_by_email(email)
        created = False

        if not user:
            # Crear usuario con contraseña aleatoria
            username = email  # Usar email como username inicial
            if self.repository.get_by_username(username):
                # Si el username existe (ej: otro email con mismo user local part), generar uno random
                username = (
                    f"{email.split('@')[0]}_{get_random_string(4)}"
                )

            random_password = get_random_string(12)
            user = self.repository.create_user(
                username=username,
                email=email,
                password=random_password,
                first_name=first_name,
                last_name=last_name,
                is_active=True,  # Activo para que pueda loguearse
            )
            created = True
            # TODO: Enviar email de bienvenida con link de setup password

        # Verificar si ya pertenece al tenant
        if TenantMembership.objects.filter(
            tenant=tenant, user=user, is_active=True
        ).exists():
            raise ValueError(
                f"El usuario {email} ya es miembro activo de este tenant."
            )

        # Crear o reactivar membresía
        membership, _ = TenantMembership.objects.update_or_create(
            tenant=tenant,
            user=user,
            defaults={
                "role": role,
                "is_active": True,
                "invited_by": invited_by,
            },
        )

        return {
            "user": user,
            "created": created,
            "membership": membership,
            "tenant": tenant,
        }
