"""
Tools para AI Core.

Este módulo importa automáticamente todas las tools para que se
registren en el ToolRegistry al importar el paquete.
"""

from .registry import ToolRegistry

# Importar todos los módulos de tools para que se auto-registren
from . import linkedin_tools  # noqa: F401
from . import candidate_tools  # noqa: F401
from . import email_tools  # noqa: F401

__all__ = [
    "ToolRegistry",
]
