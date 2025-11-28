# Resumen: Sistema de Tools en AI Core

## 📁 Estructura Implementada

```
apps/ai_core/tools/
├── __init__.py              ✅ Auto-importa todas las tools
├── registry.py              ✅ Sistema de registro (Singleton)
├── linkedin_tools.py        ✅ 3 tools de LinkedIn
├── candidate_tools.py       ✅ 3 tools de análisis de candidatos
└── email_tools.py           ✅ 3 tools de comunicación

Total: 9 tools registradas y listas para usar
```

## 🎯 Ubicación de las Tools

### Regla Simple:
**Todas las funciones Python que quieras usar como tools van en `apps/ai_core/tools/`**

### Organización por Categoría:

| Categoría | Archivo | Tools |
|-----------|---------|-------|
| **LinkedIn** | `linkedin_tools.py` | • search_linkedin_profiles<br>• get_linkedin_profile_details<br>• extract_skills_from_profile |
| **Candidatos** | `candidate_tools.py` | • analyze_candidate_fit<br>• extract_cv_information<br>• generate_candidate_summary |
| **Email** | `email_tools.py` | • send_candidate_email<br>• generate_interview_invitation_email<br>• generate_rejection_email |

## 🔧 Cómo Registrar una Tool

### Patrón de 2 Decoradores:

```python
from langchain_core.tools import tool
from .registry import ToolRegistry

@ToolRegistry.register("nombre_en_el_registro")  # 1️⃣ Registra
@tool                                              # 2️⃣ Convierte a LangChain Tool
def mi_funcion(parametro: str) -> dict:
    """Docstring obligatorio."""
    return {"resultado": parametro}
```

### ¿Por qué 2 decoradores?

1. **`@ToolRegistry.register("nombre")`**: 
   - Registra la tool en nuestro sistema interno
   - Permite obtenerla con `ToolRegistry.get_tool("nombre")`
   - Necesario para asignar tools a agentes específicos

2. **`@tool`**: 
   - Convierte la función en una LangChain Tool
   - Permite que el LLM la invoque automáticamente
   - Genera el schema para que el LLM entienda cómo usarla

## 🚀 Cómo Usar las Tools

### Opción 1: Uso Directo (Testing/Debugging)

```python
from apps.ai_core.tools import ToolRegistry

# Obtener la tool
search_tool = ToolRegistry.get_tool("linkedin_search_tool")

# Invocar
result = search_tool.invoke({
    "query": "Python Developer",
    "location": "Caracas",
    "max_results": 5
})

print(result["profiles"])
```

### Opción 2: En un Workflow (Producción)

```python
# En sourcing_graph.py
from ..tools.registry import ToolRegistry

# Configurar qué tools puede usar cada agente
agent_configs = {
    "sourcer": [
        "linkedin_search_tool",
        "get_linkedin_profile_details"
    ],
    "analyst": [
        "analyze_candidate_fit",
        "generate_candidate_summary"
    ]
}

# Obtener las tools para un agente
tool_names = agent_configs["sourcer"]
tools = [ToolRegistry.get_tool(name) for name in tool_names]

# Bind al LLM
llm_with_tools = llm.bind_tools(tools)
```

## 📝 Template para Nueva Tool

```python
# En apps/ai_core/tools/tu_categoria_tools.py

from typing import Dict
from langchain_core.tools import tool
from .registry import ToolRegistry


@ToolRegistry.register("nombre_descriptivo_de_tu_tool")
@tool
def tu_nueva_tool(
    parametro1: str,
    parametro2: int,
    opcional: str = None
) -> Dict:
    """
    Descripción clara de qué hace la tool.
    
    Esta descripción es importante porque el LLM la lee
    para decidir cuándo usar esta tool.
    
    Args:
        parametro1: Descripción del parámetro 1
        parametro2: Descripción del parámetro 2
        opcional: Parámetro opcional
    
    Returns:
        Dict con los resultados en formato estructurado
    
    Example:
        >>> result = tu_nueva_tool("test", 5)
        >>> print(result["status"])
        'success'
    """
    try:
        # Tu lógica aquí
        resultado = procesar(parametro1, parametro2)
        
        return {
            "success": True,
            "data": resultado,
            "message": "Procesado exitosamente"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Error al procesar"
        }
```

## 🔄 Flujo de Auto-Registro

```
1. Defines la función con @ToolRegistry.register() y @tool
                    ↓
2. Importas el módulo en tools/__init__.py
                    ↓
3. Al importar apps.ai_core.tools, se ejecutan los decoradores
                    ↓
4. La tool queda registrada en ToolRegistry._registry
                    ↓
5. Puedes obtenerla con ToolRegistry.get_tool("nombre")
```

## 📊 Tools Actualmente Disponibles

### LinkedIn (3 tools)
```python
# Buscar perfiles
ToolRegistry.get_tool("linkedin_search_tool")

# Obtener detalles de perfil
ToolRegistry.get_tool("get_linkedin_profile_details")

# Extraer skills
ToolRegistry.get_tool("extract_skills_from_profile")
```

### Candidatos (3 tools)
```python
# Analizar fit con vacante
ToolRegistry.get_tool("analyze_candidate_fit")

# Extraer info de CV
ToolRegistry.get_tool("extract_cv_information")

# Generar resumen
ToolRegistry.get_tool("generate_candidate_summary")
```

### Email (3 tools)
```python
# Enviar email
ToolRegistry.get_tool("send_candidate_email")

# Generar invitación a entrevista
ToolRegistry.get_tool("generate_interview_invitation_email")

# Generar email de rechazo
ToolRegistry.get_tool("generate_rejection_email")
```

## 🎓 Ejemplos Completos

Ver: `apps/ai_core/examples/usage_examples.py`

Ejecutar ejemplos:
```bash
python -m apps.ai_core.examples.usage_examples
```

## 📚 Documentación Completa

- **Arquitectura**: `docs/ai_core_architecture.md`
- **Guía de Tools**: `docs/ai_core_tools_guide.md`
- **Este Resumen**: `docs/ai_core_tools_summary.md`

## ✅ Checklist para Agregar una Nueva Tool

- [ ] Crear la función en el archivo apropiado de `tools/`
- [ ] Agregar `@ToolRegistry.register("nombre")` 
- [ ] Agregar `@tool`
- [ ] Incluir docstring completo (descripción, Args, Returns, Example)
- [ ] Usar type hints en parámetros y retorno
- [ ] Retornar Dict con estructura consistente
- [ ] Manejar errores con try/except
- [ ] Si es un nuevo archivo, importarlo en `tools/__init__.py`
- [ ] Probar con `ToolRegistry.get_tool("nombre")`
- [ ] Documentar en la guía de tools

## 🔍 Verificar Tools Registradas

```python
from apps.ai_core.tools import ToolRegistry

# Ver todas las tools
print(list(ToolRegistry._registry.keys()))

# Verificar si una tool existe
if "mi_tool" in ToolRegistry._registry:
    print("✓ Tool registrada")
else:
    print("✗ Tool no encontrada")
```

## 🎯 Próximos Pasos

1. **Implementar integraciones reales**:
   - LinkedIn API o scraping
   - SendGrid/AWS SES para emails
   - OpenAI para análisis de CVs

2. **Agregar más categorías**:
   - `web_search_tools.py` - Búsqueda web
   - `database_tools.py` - Queries a BD
   - `analytics_tools.py` - Métricas y reportes

3. **Optimizaciones**:
   - Caching de resultados
   - Rate limiting
   - Async execution

4. **Testing**:
   - Tests unitarios para cada tool
   - Tests de integración con workflows
   - Mocks para APIs externas

## 💡 Tips Importantes

1. **Nombres descriptivos**: `search_linkedin_profiles` > `search`
2. **Docstrings claros**: El LLM lee esto para decidir cuándo usar la tool
3. **Type hints siempre**: Ayuda al LLM a entender los parámetros
4. **Retornos consistentes**: Siempre Dict con `success`, `data`, `error`
5. **Manejo de errores**: Nunca dejes que una tool crashee
6. **Tenant awareness**: Si accedes a BD, filtra por tenant_id
7. **Testing**: Prueba cada tool individualmente antes de usarla en workflows

## 🆘 Troubleshooting

### "Tool no encontrada"
```python
# Verificar que esté registrada
print(ToolRegistry._registry.keys())

# Verificar que el módulo se importó
import apps.ai_core.tools
```

### "Error al invocar tool"
```python
# Verificar el schema esperado
tool = ToolRegistry.get_tool("nombre")
print(tool.args_schema)
```

### "Tool no se auto-registra"
```python
# Verificar que está en __init__.py
# apps/ai_core/tools/__init__.py
from . import tu_modulo  # noqa: F401
```
