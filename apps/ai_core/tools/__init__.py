"""
Tools para AI Core.

Este módulo importa automáticamente todas las tools para que se
registren en el ToolRegistry al importar el paquete.
"""

# Importar todos los módulos de tools para que se auto-registren
from . import (
    candidate_tools,
    email_tools,
    linkedin_tools,
)
from .registry import ToolRegistry

__all__ = [
    "ToolRegistry",
]
