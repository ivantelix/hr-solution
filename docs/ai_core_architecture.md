# Arquitectura del Módulo AI Core

## Visión General

El módulo `ai_core` es el **cerebro central y agnóstico** de la plataforma SaaS HR Solution. Su responsabilidad principal es orquestar flujos de trabajo multi-agente utilizando **LangGraph** y gestionar la conexión con diferentes proveedores de LLM (OpenAI, Claude) de forma dinámica por Tenant.

## Principios de Diseño

### 1. **Agnóstico de Dominio**
- No importa modelos de negocio específicos (como `Candidate`, `JobVacancy`)
- Recibe datos crudos (strings, dicts) como entrada
- Puede ser reutilizado en cualquier contexto de la aplicación

### 2. **Multitenant**
- Selecciona el LLM y API Key basándose en la configuración del Tenant
- Soporta BYOK (Bring Your Own Key)
- Permite a cada tenant usar su propio proveedor de IA

### 3. **Pluggable**
- Usa el patrón Factory para instanciar LLMs
- Fácil de extender con nuevos proveedores
- Desacoplamiento entre la lógica de negocio y la infraestructura de IA

### 4. **Observabilidad**
- Implementa hooks para monitoreo futuro (Langfuse/LangSmith)
- Sin acoplamiento fuerte a herramientas específicas
- Logs estructurados para debugging

## Estructura de Directorios

```
apps/ai_core/
├── __init__.py
├── apps.py                 # Configuración de la App Django
├── models/                 # Modelos de Configuración y Logs
│   ├── __init__.py
│   ├── ai_config.py        # Re-exporta TenantAIConfig de tenants
│   └── logs.py             # Auditoría de ejecución (AgentExecutionLog)
├── adapters/               # Adaptadores de Infraestructura
│   ├── __init__.py
│   ├── llm_factory.py      # Factory para instanciar OpenAI/Claude
│   └── monitoring.py       # Factory para callbacks (Langfuse/LangSmith)
├── tools/                  # Registro de Herramientas
│   ├── __init__.py
│   └── registry.py         # Decorador y Singleton para registrar tools
├── workflows/              # Definición de Grafos (LangGraph)
│   ├── __init__.py
│   └── sourcing_graph.py   # Lógica del grafo de Sourcing
└── services/               # Capa de Servicio (Entrypoint)
    ├── __init__.py
    └── workflow_service.py # Orquestador principal
```

## Componentes Principales

### 1. Modelos (`models/`)

#### TenantAIConfig
- **Ubicación Real**: `apps.tenants.models.TenantAIConfig`
- **Re-exportado desde**: `apps.ai_core.models.ai_config`
- **Propósito**: Configuración de IA por Tenant (BYOK)
- **Campos clave**:
  - `provider`: Proveedor de IA (OpenAI, Claude, Platform Default)
  - `api_key`: API Key del proveedor (encriptada en producción)
  - `model_name`: Modelo específico a usar
  - `temperature`: Temperatura para generación
  - `max_tokens`: Límite de tokens

#### AgentExecutionLog
- **Ubicación**: `apps.ai_core.models.logs`
- **Propósito**: Auditoría de cada paso de ejecución de agentes
- **Campos clave**:
  - `workflow_name`: Nombre del workflow ejecutado
  - `node_name`: Nombre del agente/nodo
  - `input_data`, `output_data`: Datos de entrada/salida (JSON)
  - `tokens_input`, `tokens_output`: Métricas de tokens
  - `cost_usd`: Costo estimado de la ejecución
  - `status`: Estado (running, success, failed)

### 2. Adaptadores (`adapters/`)

#### llm_factory.py
**Función**: `get_llm_for_tenant(tenant_config: TenantAIConfig)`

**Responsabilidad**: Devuelve una instancia de LangChain ChatModel configurada según las preferencias del tenant.

**Lógica de Fallback**:
1. Si el provider es `PLATFORM_DEFAULT`, usa OpenAI con la key global
2. Si el tenant tiene API key propia, la usa
3. Si no, usa la API key global de la plataforma

**Proveedores Soportados**:
- **OpenAI**: `ChatOpenAI` (GPT-3.5, GPT-4, etc.)
- **Claude**: `ChatAnthropic` (Claude 3, etc.)

**Ejemplo de uso**:
```python
from apps.ai_core.adapters.llm_factory import get_llm_for_tenant
from apps.tenants.models import TenantAIConfig

config = TenantAIConfig.objects.get(tenant_id=tenant_id)
llm = get_llm_for_tenant(config)
response = llm.invoke("¿Cuál es la capital de Francia?")
```

#### monitoring.py
**Función**: `get_workflow_monitor(trace_name, tenant_id, session_id=None)`

**Responsabilidad**: Devuelve una lista de Callbacks para monitorear la ejecución.

**Callbacks Incluidos**:
- **Desarrollo**: `StdOutCallbackHandler` (logs en consola)
- **Producción** (comentado): `LangfuseCallbackHandler` (observabilidad avanzada)

**Ejemplo de uso**:
```python
from apps.ai_core.adapters.monitoring import get_workflow_monitor

callbacks = get_workflow_monitor(
    trace_name="Sourcing Vacancy 123",
    tenant_id="tenant-uuid-123"
)
# Usar callbacks en la invocación del workflow
```

### 3. Herramientas (`tools/`)

#### registry.py
**Clase**: `ToolRegistry`

**Responsabilidad**: Registro centralizado de herramientas disponibles para los agentes.

**Métodos**:
- `register(name)`: Decorador para registrar una herramienta
- `get_tool(name, tenant_id=None)`: Obtiene una herramienta registrada

**Ejemplo de uso**:
```python
from apps.ai_core.tools.registry import ToolRegistry

@ToolRegistry.register("linkedin_search_tool")
def search_linkedin(query: str, tenant_id: str):
    # Lógica de búsqueda en LinkedIn
    return results

# Obtener la herramienta
tool = ToolRegistry.get_tool("linkedin_search_tool")
```

### 4. Workflows (`workflows/`)

#### sourcing_graph.py
**Clases**: `AgentState`, `SourcingWorkflowBuilder`

**Responsabilidad**: Define el flujo de trabajo multi-agente para sourcing de candidatos.

**Agentes**:
1. **Analyst**: Analiza la vacante y define criterios de búsqueda
2. **Sourcer**: Busca candidatos en LinkedIn basándose en los criterios

**Flujo**:
```
[Analyst] → [Sourcer] → [END]
```

**Tool Scoping**: Cada agente tiene acceso solo a las herramientas que necesita:
- Analyst: Sin herramientas (solo análisis)
- Sourcer: `linkedin_search_tool`

**Ejemplo de uso**:
```python
from apps.ai_core.workflows.sourcing_graph import SourcingWorkflowBuilder

builder = SourcingWorkflowBuilder(llm=llm)
app = builder.build()
result = app.invoke(initial_state)
```

### 5. Servicios (`services/`)

#### workflow_service.py
**Función**: `start_sourcing_workflow(tenant_id, vacancy_id, job_data)`

**Responsabilidad**: Orquestador principal que une todos los componentes.

**Flujo de Ejecución**:
1. Obtiene la configuración de IA del Tenant
2. Instancia el LLM correcto usando el Factory
3. Construye el grafo de LangGraph
4. Configura el monitoreo
5. Prepara el estado inicial
6. Ejecuta el workflow
7. Retorna el resultado

**Ejemplo de uso**:
```python
from apps.ai_core.services.workflow_service import start_sourcing_workflow

result = start_sourcing_workflow(
    tenant_id="tenant-uuid-123",
    vacancy_id=456,
    job_data={
        "title": "Senior Python Developer",
        "description": "...",
        "requirements": ["Python", "Django", "PostgreSQL"]
    }
)
```

## Flujo de Datos Completo

### Escenario: Sourcing de Candidatos para una Vacante

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. App de Recruitment (recruitment/services/)                  │
│    - Detecta nueva vacante                                      │
│    - Prepara job_data                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. AI Core Service (ai_core/services/workflow_service.py)      │
│    - start_sourcing_workflow(tenant_id, vacancy_id, job_data)  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Obtener Configuración del Tenant                            │
│    - TenantAIConfig.objects.get(tenant_id=tenant_id)           │
│    - Valida que existe configuración                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Factory de LLM (ai_core/adapters/llm_factory.py)            │
│    - get_llm_for_tenant(config)                                 │
│    - Retorna ChatOpenAI o ChatAnthropic                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Builder de Workflow (ai_core/workflows/sourcing_graph.py)   │
│    - SourcingWorkflowBuilder(llm=llm)                           │
│    - builder.build() → Grafo compilado                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Configurar Monitoreo (ai_core/adapters/monitoring.py)       │
│    - get_workflow_monitor(trace_name, tenant_id)                │
│    - Retorna lista de callbacks                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Ejecutar Workflow                                            │
│    - app.invoke(initial_state, config={"callbacks": monitor})   │
│                                                                  │
│    ┌──────────────┐      ┌──────────────┐                      │
│    │   Analyst    │ ───▶ │   Sourcer    │ ───▶ [END]           │
│    └──────────────┘      └──────────────┘                      │
│         │                       │                                │
│         │                       │                                │
│         ▼                       ▼                                │
│    Analiza vacante      Busca en LinkedIn                       │
│    Define criterios     Retorna candidatos                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Resultado                                                    │
│    - Lista de candidatos potenciales                            │
│    - Metadata de ejecución                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Punto de Entrada (Cómo Llamar al Módulo)

### Desde la App de Recruitment

**Archivo**: `apps/recruitment/services/sourcing_service.py` (a crear)

```python
from apps.ai_core.services.workflow_service import start_sourcing_workflow
from apps.recruitment.models import JobVacancy, Candidate

class SourcingService:
    @staticmethod
    def auto_source_candidates(vacancy_id: int, tenant_id: str):
        """
        Inicia el proceso de sourcing automático de candidatos
        para una vacante específica.
        """
        # 1. Obtener la vacante
        vacancy = JobVacancy.objects.get(id=vacancy_id, tenant_id=tenant_id)
        
        # 2. Preparar los datos para el workflow
        job_data = {
            "title": vacancy.title,
            "description": vacancy.description,
            "requirements": vacancy.requirements,
            "location": vacancy.location,
            "experience_years": vacancy.experience_years,
        }
        
        # 3. Llamar al workflow de AI Core
        result = start_sourcing_workflow(
            tenant_id=str(tenant_id),
            vacancy_id=vacancy_id,
            job_data=job_data
        )
        
        # 4. Procesar los resultados
        candidates_data = result.get("final_output", {}).get("candidates", [])
        
        # 5. Crear registros de candidatos
        for candidate_data in candidates_data:
            Candidate.objects.create(
                tenant_id=tenant_id,
                vacancy=vacancy,
                name=candidate_data["name"],
                email=candidate_data["email"],
                linkedin_url=candidate_data["linkedin_url"],
                # ... otros campos
            )
        
        return len(candidates_data)
```

### Desde una Vista o Endpoint

**Archivo**: `apps/recruitment/views/sourcing_views.py` (a crear)

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.recruitment.services.sourcing_service import SourcingService

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_auto_sourcing(request, vacancy_id):
    """
    Endpoint para iniciar el sourcing automático de candidatos.
    
    POST /api/recruitment/vacancies/{vacancy_id}/auto-source/
    """
    tenant_id = request.tenant.id  # Asumiendo middleware de tenant
    
    try:
        candidates_count = SourcingService.auto_source_candidates(
            vacancy_id=vacancy_id,
            tenant_id=tenant_id
        )
        
        return Response({
            "status": "success",
            "message": f"Se encontraron {candidates_count} candidatos",
            "candidates_count": candidates_count
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)
```

### Desde una Tarea de Celery (Asíncrono)

**Archivo**: `apps/recruitment/tasks.py` (a crear)

```python
from celery import shared_task
from apps.ai_core.services.workflow_service import start_sourcing_workflow
from apps.recruitment.models import JobVacancy

@shared_task
def async_source_candidates(vacancy_id: int, tenant_id: str):
    """
    Tarea asíncrona para sourcing de candidatos.
    """
    vacancy = JobVacancy.objects.get(id=vacancy_id, tenant_id=tenant_id)
    
    job_data = {
        "title": vacancy.title,
        "description": vacancy.description,
        # ... otros campos
    }
    
    result = start_sourcing_workflow(
        tenant_id=tenant_id,
        vacancy_id=vacancy_id,
        job_data=job_data
    )
    
    # Procesar resultado...
    return result
```

## Configuración Requerida

### Variables de Entorno (.env)

```bash
# API Keys Globales de la Plataforma (Fallback)
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...

# Langfuse (Opcional, para monitoreo en producción)
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

### Configuración en Django Settings

Ya configurado en `core/settings/base.py`:

```python
# AI Provider Configuration (LangChain)
OPENAI_API_KEY_GLOBAL = os.environ.get('OPENAI_API_KEY', '')
CLAUDE_API_KEY_GLOBAL = os.environ.get('CLAUDE_API_KEY', '')
```

### Configuración por Tenant

Cada tenant debe tener un registro en `TenantAIConfig`:

```python
from apps.tenants.models import Tenant, TenantAIConfig
from apps.tenants.models.choices import AIProvider

# Crear configuración para un tenant
tenant = Tenant.objects.get(id=tenant_id)
TenantAIConfig.objects.create(
    tenant=tenant,
    provider=AIProvider.OPENAI,  # o CLAUDE, PLATFORM_DEFAULT
    api_key="sk-tenant-specific-key",  # Opcional (BYOK)
    model_name="gpt-4-turbo",
    temperature=0.7,
    max_tokens=2000
)
```

## Dependencias

Asegúrate de instalar las dependencias en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Dependencias clave:
- `langchain` - Framework base
- `langchain-openai` - Integración con OpenAI
- `langchain-anthropic` - Integración con Claude
- `langgraph` - Orquestación de workflows multi-agente
- `langfuse` - Observabilidad (opcional)
- `redis` - Para persistencia de estado de workflows

## Próximos Pasos

### 1. Implementar Herramientas Reales
Actualmente, las herramientas están comentadas. Necesitas:
- Implementar `linkedin_search_tool`
- Registrarla en el `ToolRegistry`
- Convertirla a `StructuredTool` de LangChain

### 2. Mejorar los Agentes
Los agentes actuales son placeholders. Necesitas:
- Definir prompts específicos para cada agente
- Implementar la lógica de invocación del LLM
- Manejar los outputs de forma estructurada

### 3. Agregar Más Workflows
Crear workflows para otros casos de uso:
- Screening de candidatos
- Generación de preguntas de entrevista
- Análisis de CVs

### 4. Implementar Logging Completo
- Guardar cada ejecución en `AgentExecutionLog`
- Calcular costos reales basados en tokens
- Implementar métricas de performance

### 5. Activar Monitoreo en Producción
- Descomentar la integración con Langfuse
- Configurar las variables de entorno
- Implementar dashboards de observabilidad

## Troubleshooting

### Error: "Tenant no tiene configuración de IA"
**Solución**: Crear un `TenantAIConfig` para el tenant:
```python
TenantAIConfig.objects.create(
    tenant=tenant,
    provider=AIProvider.PLATFORM_DEFAULT
)
```

### Error: "Proveedor de IA no soportado"
**Solución**: Verificar que el `provider` en `TenantAIConfig` sea uno de los valores válidos:
- `platform_default`
- `openai`
- `claude`

### Error: API Key inválida
**Solución**: 
1. Verificar que las variables de entorno estén configuradas
2. Si el tenant usa BYOK, verificar que su API key sea válida
3. Revisar los logs para ver qué key se está usando

## Conclusión

El módulo `ai_core` proporciona una base sólida y extensible para integrar capacidades de IA en la plataforma HR Solution. Su diseño agnóstico y multitenant permite escalar fácilmente a medida que se agregan nuevos casos de uso y proveedores de IA.
