#!/bin/bash

# Script para instalar herramientas de desarrollo
# Uso: ./install_dev_tools.sh

echo "🔧 Instalando dependencias del proyecto..."

# Activar entorno virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "⚠️  No se encontró el entorno virtual en 'venv/'. Asegúrate de haberlo creado."
    exit 1
fi

# Actualizar pip
echo "📦 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias desde requirements.txt (que incluye herramientas de desarrollo)
echo "📥 Instalando paquetes desde requirements.txt..."
pip install -r requirements.txt

# Configurar pre-commit si está instalado
if command -v pre-commit &> /dev/null; then
    echo "🪝 Configurando pre-commit hooks..."
    pre-commit install
fi

echo ""
echo "✅ ¡Instalación completa!"
echo ""
echo "📝 Comandos disponibles:"
echo "  - ruff check .              # Verificar código"
echo "  - ruff check . --fix        # Arreglar automáticamente"
echo "  - ruff format .             # Formatear código"
echo "  - mypy apps/                # Type checking"
echo "  - pytest                    # Ejecutar tests"
echo ""
