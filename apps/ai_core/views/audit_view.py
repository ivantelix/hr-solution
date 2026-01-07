from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from apps.ai_core.models.ai_thread import AIConversationThread

class AIThreadAuditView(UserPassesTestMixin, View):
    """
    Vista para auditar el estado y el historial de un hilo de conversación de IA.
    Solo accesible para superusuarios o staff.
    """

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, thread_id):
        thread = get_object_or_404(AIConversationThread, thread_id=thread_id)
        
        # Recuperar el checkpoint
        checkpoint_data = thread.last_checkpoint or {}
        
        # Estructurar la respuesta para fácil lectura
        # En una impl real con LangGraph, podríamos querer reconstruir el historial de mensajes
        # desde el checkpoint si se guardó allí, o desde una DB separada de mensajes.
        # Aquí devolvemos el raw checkpoint data.
        
        response_data = {
            "thread_id": str(thread.thread_id),
            "status": thread.status,
            "created_at": thread.created_at,
            "updated_at": thread.updated_at,
            "application_id": thread.application_id,
            "checkpoint_summary": {
                "config": checkpoint_data.get("config", {}),
                # Intentar extraer mensajes si existen en la estructura estándar de LangGraph state
                # Suponiendo state.messages
                "state_snapshot": checkpoint_data.get("checkpoint", {})
            }
        }
        
        return JsonResponse(response_data)
