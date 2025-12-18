from apps.tenants.models import TenantAIConfig

from ..adapters.llm_factory import get_llm_for_tenant
from ..adapters.monitoring import get_workflow_monitor
from ..workflows.sourcing_graph import SourcingWorkflowBuilder


def start_sourcing_workflow(tenant_id: str, vacancy_id: int, job_data: dict):
    """
    Orquesta la ejecución del workflow.
    """
    # 1. Obtener Configuración del Tenant
    try:
        config = TenantAIConfig.objects.get(tenant_id=tenant_id)
    except TenantAIConfig.DoesNotExist:
        # Crear config default en memoria o lanzar error
        raise ValueError("Tenant no tiene configuración de IA") from None

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
    initial_state = {"vacancy_id": vacancy_id, "context": job_data, "messages": []}

    # 6. Ejecutar
    result = app.invoke(initial_state, config={"callbacks": monitor})

    return result
