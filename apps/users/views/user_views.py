"""
ViewSets para el modelo User.

Este módulo contiene los ViewSets de Django Rest Framework
para el modelo User, proporcionando endpoints REST para
operaciones CRUD.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.users.models import User
from apps.users.serializers import (
    ChangePasswordSerializer,
    InviteUserSerializer,
    UpdateEmailSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from apps.users.services import UserService


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.

    Proporciona endpoints REST para operaciones CRUD sobre usuarios,
    delegando la lógica de negocio al UserService.

    Endpoints:
        - GET /users/ - Lista de usuarios
        - POST /users/ - Crear usuario
        - POST /users/invite/ - Invitar usuario a tenant
        - GET /users/{id}/ - Detalle de usuario
        - PUT /users/{id}/ - Actualizar usuario completo
        - PATCH /users/{id}/ - Actualizar usuario parcial
        - DELETE /users/{id}/ - Eliminar usuario
        - POST /users/{id}/change_password/ - Cambiar contraseña
        - POST /users/{id}/update_email/ - Actualizar email
        - POST /users/{id}/verify_email/ - Verificar email
        - POST /users/{id}/deactivate/ - Desactivar usuario
        - POST /users/{id}/activate/ - Activar usuario
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    service = UserService()

    def get_permissions(self):
        """
        Obtiene los permisos según la acción.

        Returns:
            list: Lista de permisos aplicables.

        Note:
            - create (registro) es público
            - Resto de acciones requieren autenticación
        """
        if self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        """
        Obtiene el serializer según la acción.

        Returns:
            Serializer: Clase de serializer apropiada.
        """
        if self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        elif self.action == "change_password":
            return ChangePasswordSerializer
        elif self.action == "update_email":
            return UpdateEmailSerializer
        elif self.action == "invite":
            return InviteUserSerializer
        return UserSerializer

    def create(self, request: Request) -> Response:
        """
        Crea un nuevo usuario (registro).

        Args:
            request: Request con datos del usuario.

        Returns:
            Response: Usuario creado o errores de validación.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.register_user(
                username=serializer.validated_data["username"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
                phone=serializer.validated_data.get("phone"),
            )

            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def invite(self, request: Request) -> Response:
        """
        Invita a un usuario al tenant actual.

        Args:
            request: Request con email y rol.

        Returns:
            Response: Detalles de la invitación.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: Obtener tenant real del request (middleware o header)
        # Por ahora asumimos que el usuario tiene un tenant activo
        # Si tienes el TenantMiddleware implementado: request.tenant.id
        # Si no, buscamos el primer tenant activo del usuario
        user = request.user
        active_tenants = user.get_active_tenants()

        if not active_tenants.exists():
            return Response(
                {
                    "error": (
                        "No tienes ningún tenant activo para invitar usuarios."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Usamos el primer tenant activo por defecto
        # En el futuro, esto debería venir en el header X-Tenant-ID
        tenant = active_tenants.first()

        try:
            result = self.service.invite_user(
                tenant_id=tenant.id,
                email=serializer.validated_data["email"],
                role=serializer.validated_data["role"],
                invited_by=user,
                first_name=serializer.validated_data.get("first_name", ""),
                last_name=serializer.validated_data.get("last_name", ""),
            )

            message = (
                "Usuario invitado exitosamente."
                if not result["created"]
                else "Usuario creado e invitado exitosamente."
            )

            return Response(
                {
                    "message": message,
                    "user": UserSerializer(result["user"]).data,
                    "role": result["membership"].role,
                    "tenant": str(tenant.name),
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request: Request, pk=None) -> Response:
        """
        Actualiza un usuario completo.

        Args:
            request: Request con datos actualizados.
            pk: ID del usuario.

        Returns:
            Response: Usuario actualizado o error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.update_profile(
                user_id=int(pk), **serializer.validated_data
            )

            if not user:
                return Response(
                    {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request: Request, pk=None) -> Response:
        """
        Actualiza parcialmente un usuario.

        Args:
            request: Request con datos actualizados.
            pk: ID del usuario.

        Returns:
            Response: Usuario actualizado o error.
        """
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.update_profile(
                user_id=int(pk), **serializer.validated_data
            )

            if not user:
                return Response(
                    {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def change_password(self, request: Request, pk=None) -> Response:
        """
        Cambia la contraseña de un usuario.

        Args:
            request: Request con contraseñas.
            pk: ID del usuario.

        Returns:
            Response: Confirmación o error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.change_password(
                user_id=int(pk),
                old_password=serializer.validated_data["old_password"],
                new_password=serializer.validated_data["new_password"],
            )

            if not user:
                return Response(
                    {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Contraseña actualizada exitosamente"},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def update_email(self, request: Request, pk=None) -> Response:
        """
        Actualiza el email de un usuario.

        Args:
            request: Request con nuevo email.
            pk: ID del usuario.

        Returns:
            Response: Usuario actualizado o error.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = self.service.update_email(
                user_id=int(pk),
                new_email=serializer.validated_data["new_email"],
            )

            if not user:
                return Response(
                    {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def verify_email(self, request: Request, pk=None) -> Response:
        """
        Marca el email de un usuario como verificado.

        Args:
            request: Request.
            pk: ID del usuario.

        Returns:
            Response: Usuario actualizado o error.
        """
        user = self.service.verify_email(user_id=int(pk))

        if not user:
            return Response(
                {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Email verificado exitosamente"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request: Request, pk=None) -> Response:
        """
        Desactiva un usuario.

        Args:
            request: Request.
            pk: ID del usuario.

        Returns:
            Response: Confirmación o error.
        """
        user = self.service.deactivate_user(user_id=int(pk))

        if not user:
            return Response(
                {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Usuario desactivado exitosamente"}, status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"])
    def activate(self, request: Request, pk=None) -> Response:
        """
        Activa un usuario previamente desactivado.

        Args:
            request: Request.
            pk: ID del usuario.

        Returns:
            Response: Confirmación o error.
        """
        user = self.service.activate_user(user_id=int(pk))

        if not user:
            return Response(
                {"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"message": "Usuario activado exitosamente"}, status=status.HTTP_200_OK
        )
