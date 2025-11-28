# Guía de Uso: Tools en AI Core

## ¿Dónde Colocar las Tools?

Las tools deben colocarse en **`apps/ai_core/tools/`** organizadas por categoría:

```
apps/ai_core/tools/
├── __init__.py              # Auto-importa todas las tools
├── registry.py              # Sistema de registro
├── linkedin_tools.py        # ✅ Tools de LinkedIn
├── candidate_tools.py       # ✅ Tools de análisis de candidatos
├── email_tools.py           # ✅ Tools de comunicación
└── web_search_tools.py      # Tools de búsqueda web (ejemplo futuro)
```

## ¿Cómo Registrar una Tool?

### Patrón Básico

Cada tool debe usar **dos decoradores**:

1. `@ToolRegistry.register("nombre_tool")` - Registra en el sistema
2. `@tool` - Convierte la función en una LangChain Tool

### Ejemplo Completo

```python
from typing import Dict
from langchain_core.tools import tool
from .registry import ToolRegistry

@ToolRegistry.register("mi_tool_personalizada")
@tool
def mi_tool_personalizada(parametro1: str, parametro2: int) -> Dict:
    """
    Descripción clara de qué hace la tool.
    
    Args:
        parametro1: Descripción del parámetro 1
        parametro2: Descripción del parámetro 2
    
    Returns:
        Dict con los resultados
    
    Example:
        >>> result = mi_tool_personalizada("test", 5)
        >>> print(result["status"])
    """
    # Tu lógica aquí
    resultado = {
        "status": "success",
        "data": f"Procesado {parametro1} con {parametro2}"
    }
    
    return resultado
```

## Tools Implementadas

### 1. LinkedIn Tools (`linkedin_tools.py`)

#### `search_linkedin_profiles`
Busca perfiles en LinkedIn.

```python
from apps.ai_core.tools import ToolRegistry

tool = ToolRegistry.get_tool("linkedin_search_tool")
result = tool.invoke({
    "query": "Python Developer Senior",
    "location": "Caracas, Venezuela",
    "max_results": 10
})

print(result["profiles"])
```

#### `get_linkedin_profile_details`
Obtiene detalles de un perfil específico.

```python
tool = ToolRegistry.get_tool("get_linkedin_profile_details")
details = tool.invoke({
    "linkedin_url": "https://linkedin.com/in/john-doe"
})

print(details["experience"])
```

#### `extract_skills_from_profile`
Extrae y normaliza skills de un perfil.

```python
tool = ToolRegistry.get_tool("extract_skills_from_profile")
skills = tool.invoke({
    "profile_data": {
        "skills": ["Python", "Django", "python", "DJANGO"]
    }
})

print(skills)  # ['django', 'python']
```

### 2. Candidate Tools (`candidate_tools.py`)

#### `analyze_candidate_fit`
Analiza el matching entre candidato y vacante.

```python
tool = ToolRegistry.get_tool("analyze_candidate_fit")
result = tool.invoke({
    "candidate_profile": {
        "skills": ["Python", "Django", "PostgreSQL"],
        "experience_years": 5
    },
    "job_requirements": {
        "required_skills": ["Python", "Django", "FastAPI"],
        "min_experience_years": 3
    }
})

print(f"Match Score: {result['match_score']}%")
print(f"Recommendation: {result['recommendation']}")
```

#### `extract_cv_information`
Extrae información estructurada de un CV.

```python
tool = ToolRegistry.get_tool("extract_cv_information")
cv_text = """
Juan Pérez
Python Developer
Email: juan@example.com
Skills: Python, Django, PostgreSQL
"""

info = tool.invoke({"cv_text": cv_text})
print(info["skills"])
```

#### `generate_candidate_summary`
Genera un resumen ejecutivo del candidato.

```python
tool = ToolRegistry.get_tool("generate_candidate_summary")
summary = tool.invoke({
    "candidate_data": {
        "name": "Juan Pérez",
        "title": "Senior Python Developer",
        "experience_years": 8,
        "skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
        "location": "Caracas, Venezuela"
    }
})

print(summary)
```

### 3. Email Tools (`email_tools.py`)

#### `send_candidate_email`
Envía un email a un candidato.

```python
tool = ToolRegistry.get_tool("send_candidate_email")
result = tool.invoke({
    "to_email": "candidate@example.com",
    "subject": "Interview Invitation",
    "body": "We would like to invite you...",
    "tenant_id": "tenant-123"
})

print(result["success"])
```

#### `generate_interview_invitation_email`
Genera un email de invitación a entrevista.

```python
tool = ToolRegistry.get_tool("generate_interview_invitation_email")
email = tool.invoke({
    "candidate_name": "Juan Pérez",
    "position": "Python Developer",
    "interview_date": "2025-12-01",
    "interview_time": "10:00 AM",
    "company_name": "Tech Corp"
})

print(email["subject"])
print(email["body"])
```

#### `generate_rejection_email`
Genera un email de rechazo cordial.

```python
tool = ToolRegistry.get_tool("generate_rejection_email")
email = tool.invoke({
    "candidate_name": "María García",
    "position": "Backend Developer",
    "company_name": "Tech Corp",
    "personalized_feedback": "Valoramos tu experiencia en Python..."
})

print(email["body"])
```

## Cómo Usar Tools en un Workflow

### En `sourcing_graph.py`

```python
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from ..tools.registry import ToolRegistry

class AgentState(TypedDict):
    messages: List[str]
    vacancy_id: int
    context: dict
    final_output: dict

class SourcingWorkflowBuilder:
    def __init__(self, llm):
        self.llm = llm

    def build(self):
        # Configurar qué tools puede usar cada agente
        agent_configs = {
            "analyst": [
                "analyze_candidate_fit",
                "generate_candidate_summary"
            ],
            "sourcer": [
                "linkedin_search_tool",
                "get_linkedin_profile_details",
                "extract_skills_from_profile"
            ],
            "communicator": [
                "send_candidate_email",
                "generate_interview_invitation_email"
            ]
        }

        workflow = StateGraph(AgentState)

        # Crear nodos con sus tools específicas
        workflow.add_node(
            "analyst",
            self._create_node("analyst", agent_configs)
        )
        workflow.add_node(
            "sourcer",
            self._create_node("sourcer", agent_configs)
        )
        workflow.add_node(
            "communicator",
            self._create_node("communicator", agent_configs)
        )

        # Definir flujo
        workflow.set_entry_point("sourcer")
        workflow.add_edge("sourcer", "analyst")
        workflow.add_edge("analyst", "communicator")
        workflow.add_edge("communicator", END)

        return workflow.compile()

    def _create_node(self, agent_name, configs):
        # Obtener las tools asignadas a este agente
        tool_names = configs.get(agent_name, [])
        
        # Obtener las tools reales del registro
        tools = [
            ToolRegistry.get_tool(name)
            for name in tool_names
        ]
        
        # Bind tools al LLM
        llm_with_tools = self.llm.bind_tools(tools) if tools else self.llm

        def node_func(state):
            # Construir el prompt basado en el agente
            if agent_name == "sourcer":
                prompt = f"""
Eres un sourcer experto. Tu tarea es buscar candidatos para:
Posición: {state['context'].get('title')}
Requisitos: {state['context'].get('requirements')}

Usa las herramientas disponibles para encontrar candidatos.
"""
            elif agent_name == "analyst":
                prompt = f"""
Eres un analista de talento. Evalúa los candidatos encontrados
y determina cuáles son los mejores matches.
"""
            else:  # communicator
                prompt = f"""
Eres un comunicador profesional. Genera emails apropiados
para contactar a los candidatos seleccionados.
"""

            # Invocar el LLM con las tools
            response = llm_with_tools.invoke(prompt)
            
            return {
                "messages": state["messages"] + [str(response)]
            }

        return node_func
```

## Cómo Crear una Nueva Tool

### Paso 1: Crear el archivo
Crea un nuevo archivo en `apps/ai_core/tools/` o usa uno existente.

### Paso 2: Definir la función

```python
from typing import Dict
from langchain_core.tools import tool
from .registry import ToolRegistry

@ToolRegistry.register("nombre_de_tu_tool")
@tool
def tu_nueva_tool(parametro: str) -> Dict:
    """
    Descripción de tu tool.
    
    Args:
        parametro: Descripción
    
    Returns:
        Dict con resultados
    """
    # Tu lógica aquí
    return {"status": "success", "data": parametro}
```

### Paso 3: Importar en `__init__.py`

Si creaste un nuevo archivo, agrégalo en `apps/ai_core/tools/__init__.py`:

```python
from . import tu_nuevo_archivo  # noqa: F401
```

### Paso 4: Usar la tool

```python
from apps.ai_core.tools import ToolRegistry

tool = ToolRegistry.get_tool("nombre_de_tu_tool")
result = tool.invoke({"parametro": "valor"})
```

## Buenas Prácticas

### 1. Naming Convention
- Usa nombres descriptivos: `search_linkedin_profiles` ✅
- Evita nombres genéricos: `search` ❌

### 2. Type Hints
Siempre usa type hints para parámetros y retorno:
```python
def mi_tool(param: str, count: int) -> Dict:
    ...
```

### 3. Documentación
Incluye docstring completo con:
- Descripción
- Args
- Returns
- Example

### 4. Manejo de Errores
```python
@ToolRegistry.register("safe_tool")
@tool
def safe_tool(param: str) -> Dict:
    """Tool con manejo de errores."""
    try:
        # Tu lógica
        result = process(param)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 5. Tenant Awareness
Si la tool necesita acceso a datos del tenant:
```python
@ToolRegistry.register("tenant_aware_tool")
@tool
def tenant_aware_tool(param: str, tenant_id: str) -> Dict:
    """Tool que respeta el tenant."""
    # Filtrar por tenant_id
    data = Model.objects.filter(tenant_id=tenant_id, param=param)
    return {"data": list(data.values())}
```

## Verificar Tools Registradas

Para ver todas las tools disponibles:

```python
from apps.ai_core.tools import ToolRegistry

# Ver todas las tools registradas
print(ToolRegistry._registry.keys())

# Resultado:
# dict_keys([
#     'linkedin_search_tool',
#     'get_linkedin_profile_details',
#     'extract_skills_from_profile',
#     'analyze_candidate_fit',
#     'extract_cv_information',
#     'generate_candidate_summary',
#     'send_candidate_email',
#     'generate_interview_invitation_email',
#     'generate_rejection_email'
# ])
```

## Testing de Tools

### Test Unitario

```python
# tests/test_tools.py
from apps.ai_core.tools import ToolRegistry

def test_linkedin_search_tool():
    tool = ToolRegistry.get_tool("linkedin_search_tool")
    result = tool.invoke({
        "query": "Python Developer",
        "location": "Caracas",
        "max_results": 5
    })
    
    assert result["success"] is True
    assert len(result["profiles"]) <= 5
    assert result["query"] == "Python Developer"
```

### Test de Integración

```python
def test_workflow_with_tools():
    from apps.ai_core.services.workflow_service import (
        start_sourcing_workflow
    )
    
    result = start_sourcing_workflow(
        tenant_id="test-tenant",
        vacancy_id=1,
        job_data={
            "title": "Python Developer",
            "requirements": ["Python", "Django"]
        }
    )
    
    assert result is not None
```

## Próximos Pasos

1. **Implementar integraciones reales**:
   - LinkedIn API o scraping
   - Servicio de email (SendGrid, AWS SES)
   - Procesamiento de CVs con NLP

2. **Agregar más tools**:
   - Web scraping tools
   - Database query tools
   - Analytics tools

3. **Optimizar performance**:
   - Caching de resultados
   - Rate limiting
   - Async execution

4. **Mejorar seguridad**:
   - Validación de inputs
   - Sanitización de outputs
   - Permisos por tenant
