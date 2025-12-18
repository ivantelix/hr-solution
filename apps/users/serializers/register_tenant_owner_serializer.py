"""
Serializer para registro de Tenant Owner.

Este módulo maneja el registro combinado de un usuario que
automáticamente se convierte en owner de un nuevo tenant.
"""

from django.db import transaction
from rest_framework import serializers

from apps.tenants.models import Tenant, TenantMembership
from apps.tenants.models.choices import PlanType, TenantRole
from apps.users.models import User


class RegisterTenantOwnerSerializer(serializers.Serializer):
    """
    Serializer para registro de usuario como Tenant Owner.

    Este serializer maneja el registro combinado donde:
    1. Se crea un nuevo usuario
    2. Se crea un nuevo tenant
    3. El usuario se vincula como OWNER del tenant

    Este es el flujo principal para nuevos clientes de la plataforma.
    """

    # Datos del Usuario
    username = serializers.CharField(
        max_length=150,
        help_text="Nombre de usuario único",
    )
    email = serializers.EmailField(
        help_text="Correo electrónico único",
    )
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        min_length=8,
        help_text="Contraseña (mínimo 8 caracteres)",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Confirmación de contraseña",
    )
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Nombre del usuario",
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Apellido del usuario",
    )
    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        help_text="Teléfono del usuario",
    )

    # Datos del Tenant
    company_name = serializers.CharField(
        max_length=255,
        help_text="Nombre de la empresa",
    )
    company_slug = serializers.SlugField(
        max_length=255,
        help_text="Identificador único para URLs (ej: mi-empresa)",
    )
    industry = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Industria o sector de la empresa",
    )
    plan = serializers.ChoiceField(
        choices=PlanType.choices,
        default=PlanType.BASIC,
        help_text="Plan de suscripción inicial",
    )

    def validate_email(self, value: str) -> str:
        """
        Valida que el email sea único.

        Args:
            value: Email a validar.

        Returns:
            str: Email validado en minúsculas.

        Raises:
            ValidationError: Si el email ya está en uso.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value.lower()

    def validate_username(self, value: str) -> str:
        """
        Valida que el username sea único.

        Args:
            value: Username a validar.

        Returns:
            str: Username validado.

        Raises:
            ValidationError: Si el username ya está en uso.
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Este nombre de usuario ya está en uso."
            )
        return value

    def validate_company_slug(self, value: str) -> str:
        """
        Valida que el slug del tenant sea único.

        Args:
            value: Slug a validar.

        Returns:
            str: Slug validado.

        Raises:
            ValidationError: Si el slug ya está en uso.
        """
        if Tenant.objects.filter(slug=value).exists():
            raise serializers.ValidationError(
                "Este identificador de empresa ya está en uso."
            )
        return value

    def validate(self, attrs: dict) -> dict:
        """
        Valida que las contraseñas coincidan.

        Args:
            attrs: Atributos a validar.

        Returns:
            dict: Atributos validados.

        Raises:
            ValidationError: Si las contraseñas no coinciden.
        """
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data: dict) -> dict:
        """
        Crea el usuario y el tenant en una transacción atómica.

        Args:
            validated_data: Datos validados.

        Returns:
            dict: Diccionario con el usuario y tenant creados.

        Note:
            Esta operación es atómica. Si falla cualquier parte,
            se revierte toda la transacción.
        """
        # Extraer datos del usuario
        user_data = {
            "username": validated_data["username"],
            "email": validated_data["email"],
            "password": validated_data["password"],
            "first_name": validated_data.get("first_name", ""),
            "last_name": validated_data.get("last_name", ""),
            "phone": validated_data.get("phone", ""),
        }

        # Crear usuario
        user = User.objects.create_user(**user_data)

        # Extraer datos del tenant
        tenant_data = {
            "name": validated_data["company_name"],
            "slug": validated_data["company_slug"],
            "plan": validated_data.get("plan", PlanType.BASIC),
        }

        # Crear tenant
        tenant = Tenant.objects.create(**tenant_data)

        # Crear membresía como OWNER
        TenantMembership.objects.create(
            tenant=tenant,
            user=user,
            role=TenantRole.OWNER,
            is_active=True,
        )

        return {
            "user": user,
            "tenant": tenant,
        }

    def to_representation(self, instance: dict) -> dict:
        """
        Serializa la respuesta.

        Args:
            instance: Diccionario con user y tenant.

        Returns:
            dict: Representación serializada.
        """
        from apps.tenants.serializers import TenantSerializer
        from apps.users.serializers import UserSerializer

        return {
            "user": UserSerializer(instance["user"]).data,
            "tenant": TenantSerializer(instance["tenant"]).data,
            "message": (
                "Cuenta creada exitosamente. Bienvenido a la plataforma."
            ),
        }
