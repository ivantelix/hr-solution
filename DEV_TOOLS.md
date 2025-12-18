# 🛠️ Configuración de Herramientas de Desarrollo

## 📦 Instalación

### 1. Instalar herramientas de desarrollo

```bash
# Ejecutar el script de instalación
./install_dev_tools.sh
```

Esto instalará:
- ✅ **Ruff** - Linter y formatter ultra-rápido
- ✅ **mypy** - Type checker estático
- ✅ **django-stubs** - Type hints para Django
- ✅ **pytest** - Framework de testing
- ✅ **pre-commit** - Git hooks automáticos

### 2. Configurar pre-commit hooks (opcional pero recomendado)

```bash
source venv/bin/activate
pre-commit install
```

Esto ejecutará automáticamente las validaciones antes de cada commit.

---

## 🔍 Uso de Herramientas

### **Ruff** - Linter y Formatter

```bash
# Verificar código (solo mostrar errores)
ruff check .

# Arreglar automáticamente
ruff check . --fix

# Formatear código
ruff format .

# Verificar y formatear todo
ruff check . --fix && ruff format .
```

### **mypy** - Type Checking

```bash
# Verificar tipos en toda la app
mypy apps/

# Verificar una app específica
mypy apps/users/

# Verificar un archivo específico
mypy apps/users/services/user_service.py
```

### **pytest** - Testing

```bash
# Ejecutar todos los tests
pytest

# Ejecutar tests de una app
pytest apps/users/tests/

# Ejecutar con coverage
pytest --cov=apps --cov-report=html

# Ejecutar solo tests rápidos
pytest -m "not slow"
```

### **Django Check**

```bash
# Verificar configuración de Django
python manage.py check

# Verificar con todas las validaciones
python manage.py check --deploy
```

---

## 🔧 Configuración de VSCode

### Extensiones Recomendadas

Instala estas extensiones en VSCode:

1. **Python** (ms-python.python)
2. **Pylance** (ms-python.vscode-pylance)
3. **Ruff** (charliermarsh.ruff)
4. **Django** (batisteo.vscode-django)

### Configuración Manual

Si `.vscode/settings.json` está en `.gitignore`, crea el archivo manualmente con:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.extraPaths": ["${workspaceFolder}", "${workspaceFolder}/apps"],
  "ruff.enable": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

### Arreglar "Go to Definition"

Si Ctrl+Click no funciona:

1. ✅ Verifica que Pylance esté activo (esquina inferior derecha)
2. ✅ Recarga VSCode: `Ctrl+Shift+P` → "Reload Window"
3. ✅ Verifica que el intérprete sea el correcto: `Ctrl+Shift+P` → "Python: Select Interpreter" → Selecciona `./venv/bin/python`
4. ✅ Limpia caché de Pylance: `Ctrl+Shift+P` → "Pylance: Restart Server"

---

## 📋 Comandos Útiles

### Workflow Completo de Desarrollo

```bash
# 1. Activar entorno virtual
source venv/bin/activate

# 2. Verificar código
ruff check . --fix
ruff format .

# 3. Type checking
mypy apps/

# 4. Ejecutar tests
pytest

# 5. Verificar Django
python manage.py check

# 6. Si todo está bien, hacer commit
git add .
git commit -m "feat: nueva funcionalidad"
# Los pre-commit hooks se ejecutarán automáticamente
```

### Atajos

```bash
# Crear alias en ~/.bashrc o ~/.zshrc
alias lint="ruff check . --fix && ruff format ."
alias typecheck="mypy apps/"
alias test="pytest"
alias checkall="lint && typecheck && pytest && python manage.py check"
```

---

## 🎯 Estándares de Código

### Type Hints

✅ **Siempre usa type hints:**

```python
# ✅ BIEN
def get_user_by_id(self, user_id: int) -> User | None:
    return User.objects.get(id=user_id)

# ❌ MAL
def get_user_by_id(self, user_id):
    return User.objects.get(id=user_id)
```

### Docstrings

✅ **Usa Google Style docstrings:**

```python
def register_user(self, username: str, email: str) -> User:
    """
    Registra un nuevo usuario.

    Args:
        username: Nombre de usuario único.
        email: Correo electrónico único.

    Returns:
        User: Usuario creado.

    Raises:
        ValueError: Si el email ya existe.
    """
    pass
```

### Imports

✅ **Orden de imports (automático con Ruff):**

```python
# 1. Standard library
import os
from typing import Protocol

# 2. Third-party
from django.db import models
from rest_framework import serializers

# 3. First-party (tu proyecto)
from apps.users.models import User
from core.settings import BASE_DIR
```

---

## 🐛 Troubleshooting

### "Go to Definition" no funciona

```bash
# 1. Verificar pyrightconfig.json existe
ls pyrightconfig.json

# 2. Recargar VSCode
Ctrl+Shift+P → "Reload Window"

# 3. Verificar intérprete
Ctrl+Shift+P → "Python: Select Interpreter"
```

### mypy no encuentra módulos de Django

```bash
# Instalar django-stubs
pip install django-stubs[compatible-mypy]

# Verificar configuración en pyproject.toml
cat pyproject.toml | grep -A 5 "tool.mypy"
```

### Ruff no formatea al guardar

1. Verifica que la extensión Ruff esté instalada
2. Verifica `settings.json` tenga `"editor.formatOnSave": true`
3. Recarga VSCode

---

## 📚 Recursos

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Django Type Hints](https://github.com/typeddjango/django-stubs)
