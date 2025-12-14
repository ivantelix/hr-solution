#!/bin/bash

# Script para instalar herramientas de desarrollo
# Uso: ./install_dev_tools.sh

echo "🔧 Instalando herramientas de desarrollo..."

# Activar entorno virtual
source venv/bin/activate

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar herramientas de linting y type checking
echo "🔍 Instalando Ruff (linter + formatter)..."
pip install ruff

echo "🔍 Instalando mypy (type checker)..."
pip install mypy

echo "🔍 Instalando django-stubs (type stubs para Django)..."
pip install django-stubs[compatible-mypy]

echo "🔍 Instalando djangorestframework-stubs..."
pip install djangorestframework-stubs

# Instalar herramientas de testing
echo "✅ Instalando pytest y plugins..."
pip install pytest pytest-django pytest-cov pytest-mock

# Instalar pre-commit (opcional pero recomendado)
echo "🪝 Instalando pre-commit..."
pip install pre-commit

# Guardar dependencias
echo "💾 Actualizando requirements..."
pip freeze > requirements-dev.txt

echo ""
echo "✅ ¡Instalación completa!"
echo ""
echo "📝 Comandos disponibles:"
echo "  - ruff check .              # Verificar código"
echo "  - ruff check . --fix        # Arreglar automáticamente"
echo "  - ruff format .             # Formatear código"
echo "  - mypy apps/                # Type checking"
echo "  - pytest                    # Ejecutar tests"
echo "  - pre-commit install        # Configurar hooks de git"
echo ""
