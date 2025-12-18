from collections.abc import Callable
from typing import ClassVar


class ToolRegistry:
    _registry: ClassVar[dict[str, Callable]] = {}

    @classmethod
    def register(cls, name: str):
        """Decorador para registrar una herramienta."""

        def decorator(func):
            cls._registry[name] = func
            return func

        return decorator

    @classmethod
    def get_tool(cls, name: str, tenant_id: str | None = None):
        """
        Obtiene la herramienta y (opcionalmente) inyecta el tenant_id
        si la herramienta lo requiere (Currying/Partial).
        """
        func = cls._registry.get(name)
        if not func:
            raise ValueError(f"Herramienta '{name}' no registrada en ai_core.")

        # Aquí podrías aplicar lógica para inyectar tenant_id
        # automáticamente si la función lo espera. Por ahora devolvemos
        # la función cruda envuelta en una StructuredTool de LangChain.
        return func
