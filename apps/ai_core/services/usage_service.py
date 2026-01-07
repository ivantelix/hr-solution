"""
Servicio para registro de uso y costos de IA.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional

from django.db import models
from apps.ai_core.models import AgentExecutionLog
from apps.tenants.models import Tenant

logger = logging.getLogger(__name__)


class UsageService:
    """
    Servicio encargado de procesar y registrar el consumo de tokens y costos
    de las ejecuciones de agentes.
    """

    # @TODO: Pronto Antes de sacar el MVP esto debe configurarse en db en una 
    # tabla de settings administrado por un superadmin o algun otro usuario

    # Precios y Límites (Idealmente mover a DB/Settings)
    PRICING = {
        "gpt-4": {
            "input": Decimal("0.03"), "output": Decimal("0.06")
        },  # $30/1M, $60/1M (Legacy 8k)
        "gpt-4o": {
            "input": Decimal("0.005"), "output": Decimal("0.015")
        },  # $5/1M, $15/1M
        "gpt-3.5-turbo": {
            "input": Decimal("0.0005"), "output": Decimal("0.0015")
        },
        "claude-3-opus": {
            "input": Decimal("0.015"), "output": Decimal("0.075")
        },
        "default": {
            "input": Decimal("0.005"), "output": Decimal("0.015")
        },  # Default to GPT-4o
    }
    
    # Límite "hardcodeado" para MVP: $50 USD al mes por tenant
    MONTHLY_QUOTA_USD = Decimal("20.00")

    @classmethod
    def get_pricing(cls, model_name: str) -> Dict[str, Decimal]:
        """Obtiene el precio por 1K tokens para el modelo dado."""
        for key, prices in cls.PRICING.items():
            if key in model_name.lower():
                return prices
        return cls.PRICING["default"]

    @classmethod
    def check_quota(cls, tenant_id: str) -> bool:
        """
        Verifica si el tenant tiene cuota disponible para operar.
        
        Args:
            tenant_id: ID del Tenant.
            
        Returns:
            bool: True si puede operar, False si excedió la cuota.
            
        Raises:
            ValueError: Si el tenant no existe.
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            raise ValueError("Tenant no encontrado")

        # Si el tenant tiene su propia Key configurada (BYOK), no aplicamos cuota de plataforma
        try:
            if hasattr(tenant, 'ai_config') and tenant.ai_config.api_key:
                return True
        except Exception:
            pass # Si falla el acceso a ai_config, asumimos plataforma

        # Calcular consumo del mes actual (MVP: Suma total por ahora)
        # TODO: Filtrar por mes actual fecha inicio/fin
        total_spent = AgentExecutionLog.objects.filter(
            tenant=tenant
        ).aggregate(
            total=models.Sum('cost_usd')
        )['total'] or Decimal("0.00")
        
        if total_spent >= cls.MONTHLY_QUOTA_USD:
            logger.warning(f"Tenant {tenant_id} excedió su cuota: ${total_spent}")
            return False
            
        return True

    @classmethod
    def log_node_execution(
        cls,
        tenant_id: str,
        workflow_name: str,
        node_name: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]],
        metadata: Dict[str, Any],
        status: str,
        error: Optional[str] = None,
    ) -> AgentExecutionLog:
        """
        Registra la ejecución de un nodo en la bitácora.

        Args:
            tenant_id: ID del tenant.
            workflow_name: Nombre del workflow.
            node_name: Nombre del nodo/agente.
            input_data: Datos de entrada.
            output_data: Datos de salida (respuesta del LLM).
            metadata: Metadatos de la respuesta (usage, models, etc).
            status: Estado de la ejecución (success/failed).
            error: Mensaje de error si falló.

        Returns:
            AgentExecutionLog: Registro creado.
        """
        try:
            tenant = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            logger.error(f"Tenant {tenant_id} no encontrado para logging")
            return None

        # Estrategia de extracción de tokens robusta para múltiples proveedores
        # 1. Intentar key estándar de LangChain reciente 'usage_metadata'
        usage = metadata.get("usage_metadata") or {}
        
        # 2. Si encadenado, a veces está en 'token_usage'
        if not usage:
            usage = metadata.get("token_usage") or {}
            
        prompt_tokens = usage.get("input_tokens") or usage.get("prompt_tokens") or 0
        completion_tokens = usage.get("output_tokens") or usage.get("completion_tokens") or 0
        
        if not prompt_tokens:
            prompt_tokens = (
                metadata.get("input_tokens") or
                metadata.get("prompt_tokens") or 0
            )

        if not completion_tokens:
            completion_tokens = (
                metadata.get("output_tokens") or
                metadata.get("completion_tokens") or 0
            )

        # Determinar modelo usado
        model_name = metadata.get("model_name", "gpt-4o")
        pricing = cls.get_pricing(model_name)

        # Calcular costos
        input_cost = (Decimal(prompt_tokens) / 1000) * pricing["input"]
        output_cost = (Decimal(completion_tokens) / 1000) * pricing["output"]
        total_cost = input_cost + output_cost

        # Crear registro
        log_entry = AgentExecutionLog.objects.create(
            tenant=tenant,
            workflow_name=workflow_name,
            node_name=node_name,
            input_data=input_data,
            output_data=output_data,
            tokens_input=prompt_tokens,
            tokens_output=completion_tokens,
            cost_usd=total_cost,
            status=status,
        )
        
        if error:
            # Si hay error, podríamos guardarlo en output_data o un campo específico
            # Por ahora lo agregamos al output_data si es un dict, o lo encapsulamos
            if log_entry.output_data is None:
                log_entry.output_data = {"error": error}
            elif isinstance(log_entry.output_data, dict):
                log_entry.output_data["error"] = error
            log_entry.save()

        return log_entry
