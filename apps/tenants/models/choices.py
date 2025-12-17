"""
Choices para la app tenants.

Este módulo contiene las definiciones de choices (enumeraciones)
utilizadas en los modelos de tenants.
"""

from django.db import models


class PlanType(models.TextChoices):
    """
    Define los planes de suscripción disponibles.

    Attributes:
        BASIC: Plan básico con funcionalidades limitadas.
        PRO: Plan profesional con funcionalidades avanzadas.
        ENTERPRISE: Plan empresarial con todas las funcionalidades.
    """

    BASIC = "basic", "Básico"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class TenantRole(models.TextChoices):
    """
    Define los roles disponibles dentro de un tenant.

    Attributes:
        OWNER: Dueño del tenant (creador, permisos máximos).
        ADMIN: Administrador con permisos completos del tenant.
        MEMBER: Miembro con permisos limitados.
    """

    OWNER = "owner", "Dueño"
    ADMIN = "admin", "Administrador"
    MEMBER = "member", "Miembro"


class AIProvider(models.TextChoices):
    """
    Define los proveedores de IA soportados.

    Attributes:
        OPENAI: OpenAI (GPT-3.5, GPT-4, etc.).
        CLAUDE: Anthropic Claude.
        LLAMA: Meta Llama (local o API).
    """

    PLATFORM_DEFAULT = "platform_default", "Default de la Plataforma"
    OPENAI = "openai", "OpenAI"
    CLAUDE = "claude", "Anthropic Claude"
    LLAMA = "llama", "Meta Llama"
