# TODO List - HR Solution SaaS Multi-Agente

> **Fecha de Creación:** 2025-11-26  
> **Objetivo:** Refactorizar y expandir el proyecto siguiendo las especificaciones técnicas (DDD + Arquitectura Hexagonal)

---

## 🔄 FASE 1: AJUSTAR APPS EXISTENTES (users & tenants)

### 1.1. App `users` - Reestructuración DDD

- [ ] **1.1.1** Crear estructura de directorios DDD
  ```
  apps/users/
  ├── models/          # ✅ Ya existe
  ├── repositories/    # ⬅️ CREAR
  ├── services/        # ✅ Ya existe (revisar)
  ├── adapters/        # ⬅️ CREAR (para integraciones externas futuras)
  ├── views/           # ✅ Ya existe (revisar)
  └── serializers/     # ⬅️ CREAR (para DRF)
  ```

- [ ] **1.1.2** Mejorar modelo `User` con Type Hints y Docstrings
  - Agregar campos adicionales si son necesarios (phone, avatar, etc.)
  - Agregar type hints completos
  - Mejorar docstrings según estándar Google

- [ ] **1.1.3** Crear `UserRepository`
  - Implementar patrón Repository
  - Métodos: `get_by_id()`, `get_by_email()`, `filter_by_tenant()`, `create()`, `update()`
  - Incluir type hints y docstrings completos

- [ ] **1.1.4** Crear `UserService`
  - Casos de uso: `register_user()`, `update_profile()`, `deactivate_user()`
  - Usar inyección de dependencias (recibir repository)
  - Type hints y docstrings completos

- [ ] **1.1.5** Crear Serializers DRF
  - `UserSerializer` (lectura)
  - `UserCreateSerializer` (creación)
  - `UserUpdateSerializer` (actualización)

- [ ] **1.1.6** Refactorizar Views
  - Convertir a ViewSets de DRF
  - Solo validar input y delegar a Services
  - Implementar permisos y autenticación JWT

---

### 1.2. App `tenants` - Reestructuración DDD

- [ ] **1.2.1** Crear estructura de directorios DDD
  ```
  apps/tenants/
  ├── models/          # ✅ Ya existe
  ├── repositories/    # ⬅️ CREAR
  ├── services/        # ✅ Ya existe (revisar)
  ├── adapters/        # ⬅️ CREAR (para billing, analytics, etc.)
  ├── views/           # ✅ Ya existe (revisar)
  ├── serializers/     # ⬅️ CREAR
  └── middleware/      # ⬅️ CREAR (para tenant isolation)
  ```

- [ ] **1.2.2** Mejorar modelos existentes
  - **Tenant**: Agregar campos (created_at, updated_at, is_active, max_users, etc.)
  - **TenantMembership**: Agregar campos (joined_at, invited_by, is_active)
  - Agregar type hints y docstrings completos
  - Agregar métodos de negocio si son necesarios

- [ ] **1.2.3** Crear modelo `TenantAIConfig`
  - Campos: tenant (FK), provider (choices: openai, claude, llama), api_key (encrypted), model_name, temperature, max_tokens
  - Type hints y docstrings completos

- [ ] **1.2.4** Crear `TenantRepository`
  - Métodos: `get_by_id()`, `get_by_user()`, `create()`, `update()`, `get_ai_config()`
  - Type hints y docstrings completos

- [ ] **1.2.5** Crear `TenantMembershipRepository`
  - Métodos: `get_user_tenants()`, `get_tenant_members()`, `add_member()`, `remove_member()`, `update_role()`
  - Type hints y docstrings completos

- [ ] **1.2.6** Crear `TenantService`
  - Casos de uso: `create_tenant()`, `update_plan()`, `add_member()`, `remove_member()`, `configure_ai()`
  - Type hints y docstrings completos

- [ ] **1.2.7** Crear Serializers DRF
  - `TenantSerializer`
  - `TenantCreateSerializer`
  - `TenantMembershipSerializer`
  - `TenantAIConfigSerializer`

- [ ] **1.2.8** Crear Middleware de Tenant Isolation
  - `TenantMiddleware`: Intercepta JWT, extrae tenant_id, lo inyecta en request
  - Agregar a settings.MIDDLEWARE

- [ ] **1.2.9** Refactorizar Views
  - Convertir a ViewSets de DRF
  - Implementar endpoints: CRUD de tenants, gestión de membresías, configuración de IA

---

## 🆕 FASE 2: CREAR NUEVAS APPS (recruitment & ai_core)

### 2.1. App `recruitment` - Lógica de Negocio Principal

- [ ] **2.1.1** Crear estructura completa de la app
  ```
  apps/recruitment/
  ├── __init__.py
  ├── apps.py
  ├── models/
  │   ├── __init__.py
  │   ├── job_vacancy.py
  │   ├── candidate.py
  │   └── application.py
  ├── repositories/
  │   ├── __init__.py
  │   ├── job_vacancy_repository.py
  │   ├── candidate_repository.py
  │   └── application_repository.py
  ├── services/
  │   ├── __init__.py
  │   ├── job_vacancy_service.py
  │   ├── candidate_service.py
  │   └── application_service.py
  ├── adapters/
  │   ├── __init__.py
  │   ├── linkedin_adapter.py
  │   ├── whatsapp_adapter.py
  │   └── email_adapter.py
  ├── serializers/
  │   ├── __init__.py
  │   ├── job_vacancy_serializers.py
  │   ├── candidate_serializers.py
  │   └── application_serializers.py
  ├── views/
  │   ├── __init__.py
  │   ├── job_vacancy_views.py
  │   ├── candidate_views.py
  │   └── application_views.py
  ├── tasks.py
  └── agents/
      ├── __init__.py
      ├── specialist_nodes.py
      ├── workflow_graph.py
      └── tools.py
  ```

- [ ] **2.1.2** Crear modelos de dominio
  - **JobVacancy**: tenant_id, title, description, requirements, status, created_by, etc.
  - **Candidate**: tenant_id, name, email, phone, resume_url, linkedin_url, status, etc.
  - **Application**: tenant_id, job_vacancy, candidate, status, applied_at, screening_score, etc.
  - Todos con type hints y docstrings completos

- [ ] **2.1.3** Crear Repositories con aislamiento de tenant
  - Todos los repositorios reciben tenant_id en constructor
  - Aplican filtro automático por tenant_id

- [ ] **2.1.4** Crear Services con lógica de negocio
  - JobVacancyService: create, update, publish, close
  - CandidateService: create, update, import_from_linkedin
  - ApplicationService: create, update_status, calculate_score

- [ ] **2.1.5** Crear Adapters para integraciones externas
  - LinkedInAdapter: scrape_profile, search_candidates
  - WhatsAppAdapter: send_message, send_template
  - EmailAdapter: send_email, send_template

- [ ] **2.1.6** Crear Serializers DRF

- [ ] **2.1.7** Crear ViewSets DRF

- [ ] **2.1.8** Crear Tareas Celery (tasks.py)
  - `process_sourcing_task`: Buscar candidatos
  - `process_screening_task`: Evaluar candidatos
  - `process_interview_scheduling_task`: Agendar entrevistas

- [ ] **2.1.9** Crear Agentes de IA
  - `SourcingAgent`: Busca candidatos en LinkedIn
  - `ScreeningAgent`: Evalúa CVs y perfiles
  - `InterviewAgent`: Genera preguntas y evalúa respuestas

- [ ] **2.1.10** Crear Workflow Graph (LangGraph)
  - Definir nodos y edges
  - Implementar estado compartido
  - Integrar con tools

- [ ] **2.1.11** Crear Tools para agentes
  - SearchCandidatesTool
  - EvaluateCandidateTool
  - SendMessageTool

---

### 2.2. App `ai_core` - Motor Central de IA

- [ ] **2.2.1** Crear estructura completa de la app
  ```
  apps/ai_core/
  ├── __init__.py
  ├── apps.py
  ├── models/
  │   ├── __init__.py
  │   └── conversation.py  # Para guardar historial de conversaciones
  ├── adapters/
  │   ├── __init__.py
  │   ├── llm_provider.py
  │   ├── openai_adapter.py
  │   ├── claude_adapter.py
  │   └── llama_adapter.py
  ├── services/
  │   ├── __init__.py
  │   ├── llm_service.py
  │   └── orchestrator_service.py
  ├── tools/
  │   ├── __init__.py
  │   └── base_tool.py
  └── utils/
      ├── __init__.py
      ├── prompt_templates.py
      └── token_counter.py
  ```

- [ ] **2.2.2** Crear modelo `Conversation`
  - tenant_id, user_id, agent_type, messages (JSONField), created_at, updated_at

- [ ] **2.2.3** Implementar LLM Adapters
  - `OpenAIAdapter`: Integración con OpenAI API
  - `ClaudeAdapter`: Integración con Anthropic API
  - `LlamaAdapter`: Integración con Llama (local o API)
  - Todos implementan la misma interface `LLMAdapterProtocol`

- [ ] **2.2.4** Crear `LLMProviderService`
  - Selecciona el adaptador correcto según TenantAIConfig
  - Maneja BYOK (Bring Your Own Key)

- [ ] **2.2.5** Crear `OrchestratorService`
  - Orquesta la ejecución de grafos LangGraph
  - Maneja estado y persistencia

- [ ] **2.2.6** Crear herramientas base
  - `BaseTool`: Clase abstracta para todas las tools
  - Implementar interface común

- [ ] **2.2.7** Crear utilidades
  - Prompt templates reutilizables
  - Token counter para control de costos

---

## ⚙️ FASE 3: INFRAESTRUCTURA Y CONFIGURACIÓN

### 3.1. Configuración de Django

- [ ] **3.1.1** Actualizar `requirements.txt`
  - djangorestframework
  - djangorestframework-simplejwt
  - celery
  - redis
  - psycopg2-binary
  - langgraph
  - langchain
  - openai
  - anthropic
  - python-dotenv
  - pydantic

- [ ] **3.1.2** Configurar settings
  - Agregar nuevas apps a INSTALLED_APPS
  - Configurar DRF
  - Configurar JWT authentication
  - Configurar Celery
  - Configurar Redis

- [ ] **3.1.3** Crear variables de entorno (.env)
  - DATABASE_URL
  - REDIS_URL
  - SECRET_KEY
  - DEBUG
  - ALLOWED_HOSTS
  - (API keys opcionales para testing)

---

### 3.2. Docker y Orquestación

- [ ] **3.2.1** Actualizar `Dockerfile`
  - Multi-stage build
  - Optimizar capas
  - Agregar health checks

- [ ] **3.2.2** Actualizar `docker-compose.yml`
  - Servicio `web` (Django + Gunicorn)
  - Servicio `celery_worker` (Celery worker)
  - Servicio `celery_beat` (Celery scheduler - opcional)
  - Servicio `db` (PostgreSQL 15)
  - Servicio `redis` (Redis 7)
  - Configurar networks y volumes
  - Agregar health checks

- [ ] **3.2.3** Crear scripts de inicialización
  - `scripts/wait-for-it.sh`: Esperar a que DB esté lista
  - `scripts/entrypoint.sh`: Ejecutar migraciones y collectstatic

---

### 3.3. Migraciones y Datos Iniciales

- [ ] **3.3.1** Crear migraciones iniciales
  ```bash
  python manage.py makemigrations
  ```

- [ ] **3.3.2** Aplicar migraciones
  ```bash
  python manage.py migrate
  ```

- [ ] **3.3.3** Crear fixtures para datos de prueba
  - Tenant de ejemplo
  - Usuarios de ejemplo
  - JobVacancy de ejemplo
  - Candidatos de ejemplo

- [ ] **3.3.4** Crear superusuario
  ```bash
  python manage.py createsuperuser
  ```

---

## 🧪 FASE 4: TESTING Y VALIDACIÓN

### 4.1. Tests Unitarios

- [ ] **4.1.1** Tests para `users` app
  - Test UserRepository
  - Test UserService
  - Test UserViewSet

- [ ] **4.1.2** Tests para `tenants` app
  - Test TenantRepository
  - Test TenantService
  - Test TenantMiddleware
  - Test tenant isolation

- [ ] **4.1.3** Tests para `recruitment` app
  - Test Repositories
  - Test Services
  - Test Adapters (mocked)
  - Test ViewSets

- [ ] **4.1.4** Tests para `ai_core` app
  - Test LLM Adapters (mocked)
  - Test LLMProviderService
  - Test OrchestratorService

---

### 4.2. Tests de Integración

- [ ] **4.2.1** Test flujo completo de reclutamiento
  - Crear vacante → Sourcing → Screening → Interview

- [ ] **4.2.2** Test aislamiento de tenants
  - Verificar que tenant A no puede acceder a datos de tenant B

- [ ] **4.2.3** Test tareas asíncronas
  - Verificar que Celery procesa correctamente las tareas

---

## 📚 FASE 5: DOCUMENTACIÓN

- [ ] **5.1** Documentar API con Swagger/OpenAPI
  - Instalar drf-spectacular
  - Configurar schemas
  - Generar documentación automática

- [ ] **5.2** Crear README.md completo
  - Descripción del proyecto
  - Instrucciones de instalación
  - Guía de uso
  - Arquitectura

- [ ] **5.3** Documentar arquitectura
  - Diagramas de arquitectura
  - Diagramas de flujo
  - Diagramas de secuencia

- [ ] **5.4** Crear guías de desarrollo
  - Cómo agregar un nuevo agente
  - Cómo agregar una nueva tool
  - Cómo agregar un nuevo adaptador

---

## 🚀 FASE 6: DEPLOYMENT

- [ ] **6.1** Configuración de producción
  - Settings de producción
  - Configurar HTTPS
  - Configurar CORS
  - Configurar rate limiting

- [ ] **6.2** CI/CD
  - GitHub Actions / GitLab CI
  - Tests automáticos
  - Deploy automático

- [ ] **6.3** Monitoring y Logging
  - Configurar Sentry para error tracking
  - Configurar logs estructurados
  - Configurar métricas (Prometheus/Grafana)

---

## 📊 PROGRESO GENERAL

```
FASE 1: Ajustar Apps Existentes       [ ] 0/17 (0%)
FASE 2: Crear Nuevas Apps              [ ] 0/23 (0%)
FASE 3: Infraestructura                [ ] 0/11 (0%)
FASE 4: Testing                        [ ] 0/7 (0%)
FASE 5: Documentación                  [ ] 0/4 (0%)
FASE 6: Deployment                     [ ] 0/3 (0%)
─────────────────────────────────────────────────
TOTAL:                                 [ ] 0/65 (0%)
```

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

1. **Comenzar con FASE 1.1.1**: Crear estructura de directorios para `apps/users`
2. **Continuar con FASE 1.1.2**: Mejorar modelo User
3. **Seguir secuencialmente** cada tarea de la FASE 1

---

## 📝 NOTAS

- Cada tarea debe seguir los principios DDD y SOLID
- Todo el código debe tener type hints y docstrings
- Solicitar confirmación antes de ejecutar comandos destructivos
- Priorizar la seguridad y el aislamiento de tenants
- Mantener la independencia de LLM providers

---

**Última Actualización:** 2025-11-26  
**Responsable:** Ivan Castillo  
**Versión:** 1.0
