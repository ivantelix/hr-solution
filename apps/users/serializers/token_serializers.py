"""
Custom Token Serializer to inject tenant_id.
"""
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

from apps.tenants.models import TenantMembership


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        membership = TenantMembership.objects.filter(
            user=user, is_active=True
        ).first()
        if membership:
            token['tenant_id'] = str(membership.tenant.id)
            token['tenant_slug'] = membership.tenant.slug
            token['role'] = membership.role

        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # 1. Decodificar ANTES de llamar a super() para evitar error de 
        # blacklist
        refresh = RefreshToken(attrs["refresh"])
        
        tenant_id = refresh.payload.get("tenant_id")
        tenant_slug = refresh.payload.get("tenant_slug")
        role = refresh.payload.get("role")

        # 2. Llamar a la validación original (esto rota y blacklistea el token)
        data = super().validate(attrs)

        # 3. Inyectar claims en el nuevo access token
        if tenant_id:
            # Si hubo rotación, usamos el NUEVO refresh token
            if "refresh" in data:
                new_refresh = RefreshToken(data["refresh"])
                # Asegurar que los claims persistan en el nuevo refresh
                if "tenant_id" not in new_refresh.payload:
                    new_refresh["tenant_id"] = tenant_id
                    new_refresh["tenant_slug"] = tenant_slug
                    new_refresh["role"] = role
                    data["refresh"] = str(new_refresh)

                access = new_refresh.access_token
            else:
                # Si no hubo rotación, usamos el objeto original
                access = refresh.access_token

            access["tenant_id"] = tenant_id
            access["tenant_slug"] = tenant_slug
            access["role"] = role

            data["access"] = str(access)

        return data
