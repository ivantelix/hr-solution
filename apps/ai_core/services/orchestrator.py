import logging
import uuid
from typing import Optional

from django.db import transaction

from apps.tenants.models import TenantAIConfig
from apps.recruitment.models.application import Application
from apps.ai_core.models.ai_thread import AIConversationThread
from apps.ai_core.services.usage_service import UsageService
from apps.ai_core.adapters.llm_factory import get_llm_for_tenant
from apps.ai_core.workflows.sourcing_graph import SourcingWorkflowBuilder
from apps.ai_core.adapters.checkpoint_adapter import DjangoCheckpointSaver

logger = logging.getLogger(__name__)


class OrchestratorService:
    """
    Servicio central de orquestación de Agentes.
    Maneja el ciclo de vida, persistencia y control de costos.
    """

    @staticmethod
    def get_or_create_thread(application: Application) -> AIConversationThread:
        """Obtiene o crea el thread asociado a una postulación."""
        if hasattr(application, "ai_thread"):
            return application.ai_thread
        
        return AIConversationThread.objects.create(
            application=application,
            status=AIConversationThread.STATUS_ACTIVE
        )

    @staticmethod
    def run_sourcing_process(vacancy_id: int, application_id: int, tenant_id: str):
        """
        Ejecuta o reanuda el proceso de sourcing para un candidato específico.
        """
        try:
            application = Application.objects.get(id=application_id, tenant_id=tenant_id)
        except Application.DoesNotExist:
            raise ValueError("Application/Tenant match not found")

        # 1. Validación de Créditos
        if not UsageService.check_quota(str(tenant_id)):
            # Si no hay créditos, pausamos el thread si existe
            if hasattr(application, "ai_thread"):
                application.ai_thread.status = AIConversationThread.STATUS_PAUSED_NO_CREDITS
                application.ai_thread.save()
            raise ValueError("Insufficient credits to run AI process")

        # 2. Configuración de Thread y Persistencia
        thread = OrchestratorService.get_or_create_thread(application)
        
        # Si estaba pausado por error o creditos, lo reactivamos
        if thread.status != AIConversationThread.STATUS_ACTIVE:
            thread.status = AIConversationThread.STATUS_ACTIVE
            thread.save()

        # 3. Setup de infraestructura AI (LLM + Checkpointer)
        try:
            ai_config = TenantAIConfig.objects.get(tenant_id=tenant_id)
        except TenantAIConfig.DoesNotExist:
            ai_config = None

        llm = get_llm_for_tenant(ai_config)
        checkpointer = DjangoCheckpointSaver()
        
        builder = SourcingWorkflowBuilder(llm=llm, checkpoint_saver=checkpointer)
        app = builder.build()

        # 4. Construcción del Estado Inicial
        # Si ya existe historia, LangGraph la recuperará vía checkpointer + thread_id
        # Solo inyectamos el contexto necesario si es una nueva corrida o reanudación
        
        config = {"configurable": {"thread_id": str(thread.thread_id)}}
        
        # Datos del job para contexto (simplificado, idealmente fetch de JobVacancy)
        job_Vacancy = application.vacancy
        job_data = {
            "title": job_Vacancy.title,
            "requirements": job_Vacancy.requirements, # Asumiendo campo existe
            "analysis_type": "FLEXIBLE", # O obtener de vacancy settings
        }
        
        initial_state = {
            "vacancy_id": vacancy_id,
            "context": {
                **job_data,
                "tenant_id": str(tenant_id),
                "analysis_type": job_data.get("analysis_type", "FLEXIBLE")
            },
            # No enviamos 'messages' vacíos si queremos reanudar, LangGraph maneja esto
            # Si es nuevo, LangGraph iniciará vacío.
        }

        # 5. Ejecución (Invoke)
        # Usamos invoke con config para persistencia
        final_state = app.invoke(initial_state, config=config)
        
        # 6. Post-Procesamiento
        # Actualizar estado de Application según resultado
        if final_state.get("is_qualified") is False:
             # Si el analista lo descartó
             if hasattr(application, "status"):
                 # Update status logic here if needed
                 pass
        
        return final_state
