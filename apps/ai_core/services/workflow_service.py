from apps.tenants.models import TenantAIConfig

from ..adapters.llm_factory import get_llm_for_tenant
from ..adapters.monitoring import get_workflow_monitor
from ..services.usage_service import UsageService
from ..workflows.sourcing_graph import SourcingWorkflowBuilder


def start_sourcing_workflow(tenant_id: str, vacancy_id: int, job_data: dict):
    """
    Orquesta la ejecución del workflow.
    """
    # 1. Verificar Cuota
    if not UsageService.check_quota(str(tenant_id)):
        raise ValueError("Has alcanzado el límite de tu plan. Por favor contacta a soporte.")

    # 2. Obtener Configuración (Puede ser None, el factory se encarga)
    try:
        config = TenantAIConfig.objects.get(tenant_id=tenant_id)
    except TenantAIConfig.DoesNotExist:
        config = None

    # 2. Instanciar el LLM correcto (Factory)
    llm = get_llm_for_tenant(config)

    # 3. Construir el Grafo
    builder = SourcingWorkflowBuilder(llm=llm)
    app = builder.build()

    # 4. Configurar Monitoreo
    monitor = get_workflow_monitor(
        trace_name=f"Sourcing Vacancy {vacancy_id}", tenant_id=str(tenant_id)
    )

    # 5. Estado Inicial
    # Inyectamos tenant_id en el contexto para logging
    job_data_with_context = job_data.copy()
    job_data_with_context["tenant_id"] = str(tenant_id)
    
    initial_state = {
        "vacancy_id": vacancy_id,
        "context": job_data_with_context,
        "messages": []
    }

    # 6. Ejecutar
    result = app.invoke(initial_state, config={"callbacks": monitor})

    return result
