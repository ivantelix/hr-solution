from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver, Checkpoint, CheckpointMetadata, CheckpointTuple
)

from apps.ai_core.models.ai_thread import AIConversationThread


class DjangoCheckpointSaver(BaseCheckpointSaver):
    """
    Adaptador para persistir el estado de LangGraph.
    """
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """
        Recupera el último checkpoint válido para el thread_id dado.
        """
        thread_id = config["configurable"].get("thread_id")
        if not thread_id:
            return None

        try:
            thread = AIConversationThread.objects.get(thread_id=thread_id)
            if not thread.last_checkpoint:
                return None

            checkpoint_data = thread.last_checkpoint

            # Mock functional return
            return CheckpointTuple(
                config=config,
                checkpoint=checkpoint_data.get("checkpoint"),
                metadata=checkpoint_data.get("metadata"),
                parent_config=checkpoint_data.get("parent_config")
            )

        except AIConversationThread.DoesNotExist:
            return None

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: Dict[str, Any],
    ) -> RunnableConfig:
        """
        Guarda el checkpoint actual en la base de datos.
        """
        thread_id = config["configurable"].get("thread_id")
        if not thread_id:
            return config

        try:
            thread = AIConversationThread.objects.get(thread_id=thread_id)

            data_to_save = {
                "checkpoint": checkpoint,
                "metadata": metadata,
                "parent_config": config
            }

            thread.last_checkpoint = data_to_save
            thread.save(update_fields=["last_checkpoint", "updated_at"])

            return {
                "configurable": {
                    "thread_id": thread_id,
                    "thread_ts": checkpoint.get("id"),
                }
            }

        except AIConversationThread.DoesNotExist:
            pass

        return config

    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ):
        """Requerido por la interfaz pero no crítico para este MVP."""
        return []
