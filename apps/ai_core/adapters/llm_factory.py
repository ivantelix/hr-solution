from django.conf import settings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models.ai_config import TenantAIConfig
from langchain_openai import ChatOpenAI

from apps.tenants.models.choices import AIProvider


def get_llm_for_tenant(tenant_config: TenantAIConfig):
    """
    Devuelve una instancia de LangChain ChatModel configurada
    según las preferencias del tenant o la plataforma.
    """
    # 1. Determinar configuración (BYOK vs Plataforma)
    api_key = None
    provider = None
    model_name = None

    if tenant_config and tenant_config.api_key:
        # BYOK: El cliente trae su propia llave
        api_key = tenant_config.api_key
        provider = tenant_config.provider
        model_name = tenant_config.model_name
    else:
        # Plataforma: Usar llaves maestras
        # TODO: Aquí podríamos validar cuotas antes de asignar
        provider = AIProvider.OPENAI  # Default de plataforma
        api_key = settings.OPENAI_API_KEY_GLOBAL
        model_name = "gemini-1.5-flash"  # Default de plataforma
    
    if not api_key:
        raise ValueError("No se encontró una API Key válida (ni del tenant ni global).")

    # 2. Instanciar Modelo
    if provider == AIProvider.OPENAI:
        return ChatOpenAI(api_key=api_key, model=model_name, temperature=0)

    elif provider == AIProvider.CLAUDE:
        return ChatAnthropic(api_key=api_key, model=model_name, temperature=0)

    elif provider == AIProvider.GEMINI:
        return ChatGoogleGenerativeAI(
            google_api_key=api_key,
            model=model_name,
            temperature=0
        )

    raise ValueError(f"Proveedor de IA no soportado: {provider}")
