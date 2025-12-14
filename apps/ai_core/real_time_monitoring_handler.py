from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from langchain_core.callbacks import BaseCallbackHandler


class RealTimeMonitoringHandler(BaseCallbackHandler):
    def __init__(self, tenant_id, vacancy_id):
        self.channel_layer = get_channel_layer()
        self.group_name = f"vacancy_{tenant_id}_{vacancy_id}"

    def on_chain_start(self, serialized, inputs, **kwargs):
        self._send_update("status", "Workflow iniciado...")

    def on_tool_start(self, serialized, input_str, **kwargs):
        # El usuario ve qué herramienta se está usando
        tool_name = serialized.get("name")
        self._send_update("tool_start", f"Ejecutando herramienta: {tool_name}")

    def on_chain_end(self, outputs, **kwargs):
        self._send_update("success", "Proceso completado.")

    def _send_update(self, type, message):
        # Envía el mensaje al WebSocket
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                # Método en Consumer de Django Channels
                "type": "agent_update",
                "data": {"status": type, "message": message},
            },
        )
