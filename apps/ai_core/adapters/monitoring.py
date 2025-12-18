# import os
from django.conf import settings
from langchain_core.callbacks import StdOutCallbackHandler

# from langfuse.callback import CallbackHandler as LangfuseCallbackHandler


def get_workflow_monitor(
    trace_name: str, tenant_id: str, session_id: str | None = None
) -> list:
    """
    Devuelve una lista de Callbacks para monitorear la ejecución.
    """
    callbacks = []

    # 1. Logs de consola en desarrollo
    if settings.DEBUG:
        callbacks.append(StdOutCallbackHandler())

    # 2. Hook para Langfuse (Descomentar en producción)
    """
    if os.environ.get("LANGFUSE_PUBLIC_KEY"):
        langfuse_handler = LangfuseCallbackHandler(
            secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
            public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
            host=os.environ.get("LANGFUSE_HOST"),
            trace_name=trace_name,
            user_id=str(tenant_id),
            session_id=session_id
        )
        callbacks.append(langfuse_handler)
    """

    return callbacks
