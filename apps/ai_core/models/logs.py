from django.db import models
from apps.tenants.models import Tenant


class AgentExecutionLog(models.Model):
    """
    Bitácora de cada paso que da un agente.
    """
    STATUS_RUNNING = "running"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_RUNNING, "Running"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    # Ej: "sourcing_workflow"
    workflow_name = models.CharField(max_length=100)

    # Ej: "screening_agent"
    node_name = models.CharField(max_length=100)

    # Inputs y Outputs (JSON grandes)
    input_data = models.JSONField()
    output_data = models.JSONField(null=True)

    # Métricas clave
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    duration_seconds = models.FloatField(null=True)

    # Costos (Vital para tu SaaS)
    tokens_input = models.IntegerField(default=0)
    tokens_output = models.IntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, default=0)

    status = models.CharField(
        max_length=20,
        default=STATUS_RUNNING,
        choices=STATUS_CHOICES
    )

    def __str__(self):
        return f"{self.workflow_name} - {self.status}"
