
# Test-Flow-Manually

Esta guía detalla el paso a paso para probar manualmente el flujo de **Sourcing AI** que hemos refactorizado.

> [!IMPORTANT]
> **Alcance Actual**: El flujo implementado (`SourcingWorkflow`) se encarga de **Analizar Requisitos** y **Buscar Candidatos (Sourcing)**.
> - La funcionalidad de **Publicar Vacante (Posting)** en redes sociales no está incluída en este grafo de IA (es un flujo separado).
> - La integración con Redes Sociales (LinkedIn) utiliza actualmente **Datos Simulados (Mock)**. No se requiere autenticación OAuth real ni realizar posts reales en LinkedIn para esta prueba.

## 1. Configuración Inicial (Variables y Credenciales)

Asegúrate de tener las siguientes variables en tu entorno (archivo `.env` o exportadas en shell):

- **LLM Provider**:
  - `OPENAI_API_KEY`: Tu key real (si usas OpenAI).
  - `GEMINI_API_KEY`: Tu key real (si usas Gemini).
  - *Nota*: El sistema está configurado por defecto para buscar `OPENAI_API_KEY_GLOBAL` en `settings`, pero soporta BYOK.

- **Seguridad**:
  - `FERNET_KEY`: (Opcional) Si no la defines, el sistema usará una key de desarrollo por defecto.

- **Servicios Externos**:
  - **Celery/Redis**: Aunque la configuración existe en `settings.py`, la prueba manual que haremos ejecutará el proceso de forma **Síncrona** en la shell, por lo que no necesitas tener los workers de Celery corriendo obligatoriamente ahora mismo.

## 2. Creación del Tenant (Inquilino)

Debemos crear la "empresa" que usará el sistema.

**Vía Django Shell (`python3 manage.py shell`):**

```python
from apps.tenants.models import Tenant, TenantAIConfig

# 1. Crear Tenant
# 1. Crear Tenant
tenant, _ = Tenant.objects.get_or_create(
    name="Empresa Prueba",
    slug="prueba-com", # Usamos slug como identificador
    defaults={
        "is_active": True,
        "max_users": 10
    }
)

# 2. Configurar IA para el Tenant
# Aquí defines qué motor usará. Si tienes key de OpenAI/Gemini, ponla aquí (o usa la global).
ai_config, _ = TenantAIConfig.objects.get_or_create(
    tenant=tenant,
    defaults={
        "provider": "openai", # o "gemini", "claude"
        "model_name": "gpt-4o",
        "api_key": "tu api key" # Opcional si usas settings globales
    }
)
print(f"Tenant ID: {tenant.id}")
```

## 3. Creación y Configuración de la Vacante

Creamos el puesto de trabajo que el agente analizará.

```python
from apps.recruitment.models import JobVacancy

vacancy = JobVacancy.objects.create(
    tenant=tenant,
    title="Desarrollador Python Senior",
    description="Se busca experto en Django, DRF, Celery y LangGraph. Mínimo 5 años de experiencia.",
    # status="OPEN", # Asegúrate de que tenga un estado activo
)
print(f"Vacancy ID: {vacancy.id}")
```

## 4. Conexión Redes Sociales (OAuth) - Estado Actual

> [!NOTE]
> **Simulación**: Actualmente, el módulo de herramientas (`linkedin_tools.py`) está en modo **MOCK**.
> Esto significa que:
> 1. No necesitas hacer login real con OAuth.
> 2. No se publicará nada real en LinkedIn.
> 3. El agente "simulará" que busca candidatos en LinkedIn y devolverá perfiles de prueba generados por código.

**Para probar:** No necesitas configurar nada extra aquí. El agente usará las herramientas simuladas automáticamente.

## 5. Simular Flujo de "Postulación" (Sourcing)

En un flujo real, un candidato llegaría por un Post. En esta prueba manual, creamos el candidato y la postulación ("Application") directamente para que la IA la procese.

```python
from apps.recruitment.models import Candidate, Application

# Creamos un candidato que "se postuló"
candidate = Candidate.objects.create(
    tenant=tenant,
    first_name="Juan",
    last_name="Perez",
    email="juan.perez@test.com",
    linkedin_url="https://linkedin.com/in/juanperez-test" # URL simulada
)

# Creamos la postulación (Application)
application = Application.objects.create(
    tenant=tenant,
    vacancy=vacancy,
    candidate=candidate
)
print(f"Application ID: {application.id}")
```

## 6. Ejecución del Workflow AI (Orchestrator)

Ahora invocamos manualmente al cerebro ("Orchestrator") para que analice esta postulación.

```python
from apps.ai_core.services.orchestrator import OrchestratorService

print("Iniciando análisis de IA...")

# Ejecución Síncrona (esperará a que termine)
state_result = OrchestratorService.run_sourcing_process(
    vacancy_id=vacancy.id,
    application_id=application.id,
    tenant_id=tenant.id
)

print("¡Flujo terminado!")
print("Resultado Final:", state_result)
# Deberías ver 'is_qualified': True/False y mensajes del analista.
```

## 7. Verificación y Seguimiento (Audit View)

Una vez ejecutado, puedes ver la traza persistente:

1.  **Levanta el servidor**:
    ```bash
    python3 manage.py runserver
    ```

2.  **Obtén el ID del Thread**:
    ```python
    # En la shell anterior
    print(f"Thread ID: {application.ai_thread.thread_id}")
    ```

3.  **Visita la URL de Auditoría**:
    Abre en tu navegador: `http://localhost:8000/ai/audit/<TU-THREAD-ID>/`

    Allí verás el JSON con el estado final ("checkpoint"), confirmando que la IA recordó y guardó todo el proceso.

4.  **Verificar Costos**:
    Revisa la tabla de logs en shell:
    ```python
    from apps.ai_core.models import AgentExecutionLog
    logs = AgentExecutionLog.objects.filter(tenant=tenant)
    for log in logs:
        print(f"Nodo: {log.node_name} | Costo: ${log.cost_usd} | Tokens: {log.total_tokens}")
    ```

---

### Resumen de Configuración Extra

- **Celery**: No requerido para esta prueba manual síncrona.
- **URLs Exponibles**: No requerido (usamos localhost).
- **OAuth Callbacks**: No requerido (Mock Mode).

Todo está listo para probarse localmente con `manage.py shell`.
