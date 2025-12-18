from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from ..models.ai_config import TenantAIConfig
from apps.tenants.models.choices import AIProvider


def get_llm_for_tenant(tenant_config: TenantAIConfig):
    """
    Devuelve una instancia de LangChain ChatModel configurada
    según las preferencias del tenant.
    """
    api_key = tenant_config.api_key
    provider = tenant_config.provider
    model_name = tenant_config.model_name

    # Lógica de Fallback a las llaves globales de la plataforma
    if provider == AIProvider.PLATFORM_DEFAULT:
        # Aquí podrías definir tu lógica de default (ej. usar OpenAI)
        provider = AIProvider.OPENAI
        api_key = settings.OPENAI_API_KEY_GLOBAL

    # 1. OpenAI
    if provider == AIProvider.OPENAI:
        final_key = api_key or settings.OPENAI_API_KEY_GLOBAL
        return ChatOpenAI(api_key=final_key, model=model_name, temperature=0)

    # 2. Claude
    elif provider == AIProvider.CLAUDE:
        final_key = api_key or settings.CLAUDE_API_KEY_GLOBAL
        return ChatAnthropic(
            api_key=final_key,
            model=model_name, temperature=0
        )

    # 3. Gemini
    elif provider == AIProvider.GEMINI:
        final_key = api_key or settings.GEMINI_API_KEY_GLOBAL
        return ChatGoogleGenerativeAI(
            google_api_key=final_key,
            model=model_name,
            temperature=0
        )

    raise ValueError(f"Proveedor de IA no soportado: {provider}")
