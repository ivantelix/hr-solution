import uuid
from django.db import models
from apps.recruitment.models.application import Application

class AIConversationThread(models.Model):
    """
    Modelo para persistencia del hilo de conversación de LangGraph.
    Permite pausar y reanudar flujos.
    """
    STATUS_ACTIVE = "active"
    STATUS_PAUSED_NO_CREDITS = "paused_no_credits"
    STATUS_ERROR = "error"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED_NO_CREDITS, "Paused (No Credits)"),
        (STATUS_ERROR, "Error"),
        (STATUS_COMPLETED, "Completed"),
    ]

    thread_id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False
    )

    application = models.OneToOneField(
        Application,
        on_delete=models.CASCADE,
        related_name="ai_thread",
        verbose_name="Postulación"
    )

    # Checkpoint serializado (puede ser JSON binario dependiendo del
    # serializer de LangGraph). Por simplicidad usaremos JSONField.
    last_checkpoint = models.JSONField(null=True, blank=True)

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread {self.thread_id} - {self.status}"
