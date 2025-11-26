# Documento de Especificación Técnica: SaaS de Reclutamiento Multi-Agente con IA

## 1. Resumen Ejecutivo

Desarrollo de una plataforma SaaS multitenant diseñada para automatizar flujos de reclutamiento (Sourcing, Screening, Entrevistas) mediante un sistema multi-agente. La arquitectura prioriza la escalabilidad, el aislamiento de datos por cliente y la independencia tecnológica de los modelos de lenguaje (LLMs).

---

## 2. Stack Tecnológico

- **Backend Framework:** Django 5+ (Python 3.11+)
- **API Framework:** Django Rest Framework (DRF)
- **Base de Datos:** PostgreSQL 15+ (Arquitectura Shared-Database)
- **Tareas Asíncronas:** Celery + Redis (Broker)
- **Orquestación de IA:** LangGraph (para grafos de agentes con estado)
- **Infraestructura:** Docker & Docker Compose
- **Entorno de Desarrollo:** Windsurf (AI IDE)

---

## 3. Arquitectura del Sistema

Se implementa una **Arquitectura Hexagonal (Puertos y Adaptadores)** fusionada con principios de **Domain-Driven Design (DDD)** para desacoplar la lógica de negocio de la infraestructura.

### 3.1. Estructura de Directorios (Modular)

El proyecto evita el patrón monolítico de Django. Se divide en apps que actúan como **Bounded Contexts**.

```
/
├── core/                   # Configuración del Proyecto (Settings)
│   ├── settings/           # Configuración dividida (base, dev, prod, test)
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Bounded Contexts
│   ├── users/              # Gestión de Identidad (Auth)
│   ├── tenants/            # Gestión de SaaS (Clientes, Planes, Memberships)
│   ├── recruitment/        # Lógica de Negocio (Vacantes, Candidatos)
│   └── ai_core/            # Motor Central de IA (Orquestación, LLMs)
├── docker-compose.yml      # Orquestación de servicios (Web, DB, Worker, Redis)
├── Dockerfile              # Imagen de la aplicación
└── manage.py
```

### 3.2. Capas de la Aplicación (DDD) dentro de cada App

Cada app (recruitment, ai_core) sigue esta estructura interna:

```
/apps/recruitment/
├── models/         # Dominio: Entidades y lógica de estado puro
├── repositories/   # Infraestructura: Abstracción del ORM
├── adapters/       # Infraestructura: Comunicación con APIs externas
├── services/       # Aplicación: Casos de Uso
├── views/          # Infraestructura: Capa de presentación (HTTP)
├── tasks.py        # Tareas asíncronas para Celery
└── agents/         # Motor de IA (específico para recruitment)
    ├── __init__.py
    ├── specialist_nodes.py  # SourcingAgent, ScreeningAgent
    ├── workflow_graph.py    # Grafo de LangGraph
    └── tools.py             # Herramientas para agentes
```

#### Responsabilidades por Capa:

- **models/ (Dominio):** Entidades y lógica de estado puro. No contienen lógica externa.
- **services/ (Aplicación):** Casos de Uso. Orquestan la lógica llamando a Repositorios y Adaptadores.
- **repositories/ (Infraestructura):** Abstracción del ORM. El servicio pide datos al repo, no al modelo directamente.
- **adapters/ (Infraestructura):** Comunicación con el mundo exterior (APIs de OpenAI, LinkedIn, WhatsApp).
- **views/ (Infraestructura):** Capa de presentación (HTTP). Solo valida input y llama a Tareas o Servicios.
- **tasks.py:** Definición de tareas asíncronas para Celery.

---

## 4. Estrategia Multitenant

Se utiliza el modelo **Base de Datos Compartida, Esquema Compartido** para eficiencia de costos y mantenimiento.

### 4.1. Aislamiento de Datos

- **Identificación:** Middleware intercepta el JWT, extrae el `tenant_id` y lo inyecta en el `request`.
- **Persistencia:** Todos los modelos críticos (JobVacancy, Candidate) tienen un campo obligatorio `tenant_id`.
- **Repositorios Seguros:** El aislamiento se aplica en la capa de Repositorio. El repositorio requiere el `tenant_id` en su constructor y lo aplica automáticamente a todos los filtros `.filter(tenant_id=self.tenant_id)`.

### 4.2. Modelos Clave (apps/tenants)

- **Tenant:** Representa a la Pyme/Cliente. Define el plan (Basic, Pro, Enterprise).
- **TenantMembership:** Tabla intermedia que vincula User con Tenant y define el role (Admin, Member).

---

## 5. Orquestación de Agentes y IA (apps/ai_core)

La lógica de IA está centralizada en una app dedicada (`ai_core`) para ser reutilizable y agnóstica al negocio de reclutamiento.

### 5.1. Flujo de Ejecución Asíncrono

1. **Trigger:** Usuario hace POST a la API (recruitment).
2. **Cola:** La vista envía una tarea a **Celery** (tasks.py).
3. **Worker:** Un proceso worker ejecuta la tarea.
4. **Orquestación:** La tarea llama a `ai_core` para iniciar un grafo de **LangGraph**.
5. **Ejecución:** Los nodos del grafo (Agentes) ejecutan herramientas y actualizan el estado.

### 5.2. Independencia del Modelo (Pattern Provider)

El sistema es agnóstico al LLM (OpenAI, Claude, Llama).

- **TenantAIConfig:** Modelo donde cada cliente configura su proveedor preferido y API Key (BYOK - Bring Your Own Key).
- **LLMProvider:** Servicio que instantiates el adaptador correcto (OpenAIAdapter, ClaudeAdapter) basado en la configuración del tenant en tiempo de ejecución.

### 5.3. Herramientas (Tools)

Los agentes no interactúan con la DB directamente. Usan "Tools" que envuelven a los **Repositorios** y **Adaptadores** del sistema.

---

## 6. Infraestructura y Despliegue (Docker)

El sistema se orquesta mediante docker-compose con cuatro servicios principales:

1. **web:** Contenedor Django corriendo con Gunicorn (maneja peticiones HTTP).
2. **celery_worker:** Contenedor Django corriendo Celery (maneja agentes de IA y tareas pesadas).
3. **db:** Contenedor PostgreSQL 15.
4. **redis:** Contenedor Redis (Broker de mensajes para Celery).

---

## 7. Reglas de Desarrollo

### 7.1. ROL Y OBJETIVO

**Actúa como un Ingeniero de Software Senior Especialista en Python y Arquitecto de Integraciones de Inteligencia Artificial.** Tu objetivo principal es asistir en la escritura de código robusto, escalable y mantenible, priorizando la arquitectura limpia y la seguridad operativa.

### 7.2. REGLAS DE ARQUITECTURA Y DISEÑO (DDD & SOLID)

#### Implementación Estricta de DDD (Domain-Driven Design):

- Estructura el proyecto separando claramente las capas: **Dominio** (Lógica de negocio pura, entidades), **Aplicación** (Casos de uso), e **Infraestructura** (Bases de datos, APIs externas, Frameworks).
- El código del dominio **no debe depender** de la infraestructura. Utiliza interfaces y abstracciones.
- Utiliza el _Lenguaje Ubicuo_ del negocio en el nombrado de clases y métodos.

#### Principios SOLID:

- **SRP (Single Responsibility Principle):** Cada clase o función debe tener una única responsabilidad.
- **OCP (Open/Closed Principle):** El código debe estar abierto a la extensión pero cerrado a la modificación.
- **LSP (Liskov Substitution Principle):** Las subclases deben ser sustituibles por sus clases base sin alterar el comportamiento.
- **ISP (Interface Segregation Principle):** Prefiere muchas interfaces específicas a una interfaz de propósito general.
- **DIP (Dependency Inversion Principle):** Depende de abstracciones, no de concreciones (Inyección de Dependencias).

### 7.3. ESTÁNDARES DE CÓDIGO (PEP 8 Y BUENAS PRÁCTICAS)

#### Cumplimiento de PEP 8:

- Usa `snake_case` para variables y funciones, y `CamelCase` para clases.
- Mantén la longitud de línea legible (sugerido 88 o 120 caracteres).
- Organiza las importaciones: Librería estándar > Terceros > Locales.

#### Modern Python & Type Hinting:

- Utiliza **Type Hints** en todas las firmas de funciones y definiciones de variables (Python 3.10+ sintaxis preferida, ej: `str | None` en lugar de `Optional[str]`).
- Usa Dataclasses o Pydantic para objetos de transferencia de datos (DTOs).

#### Documentación:

- Incluye _Docstrings_ explicativos (formato Google o NumPy) en todas las clases y métodos públicos, detallando argumentos, retornos y excepciones.

### 7.4. SEGURIDAD Y FLUJO DE TRABAJO (CONFIRMACIONES)

#### Protocolo de Ejecución de Comandos (CRÍTICO):

**SIEMPRE solicita confirmación explícita** al usuario antes de:

- Ejecutar comandos de terminal que modifiquen el sistema de archivos (rm, mv, chmod).
- Instalar nuevas dependencias (pip install, poetry add).
- Realizar commits o push a repositorios Git.
- Desplegar servicios o contenedores Docker.

Muestra el comando exacto que planeas ejecutar y espera un "Sí/Proceder".

### 7.5. ESPECIALIZACIÓN EN IA

- Al integrar APIs de IA (OpenAI, Anthropic, HuggingFace), encapsula la lógica en servicios de infraestructura.
- Maneja las claves de API (API Keys) exclusivamente a través de variables de entorno (.env), nunca hardcodeadas.
- Implementa manejo de errores robusto para fallos de red o límites de cuota (Rate Limits).

### 7.6. MODULARIDAD Y GRANULARIDAD DE ARCHIVOS

#### Principio de Un Archivo por Clase/Funcionalidad:

- **Regla General:** Cada clase debe estar en su propio archivo dedicado.
- **Beneficios:**
  - Mayor legibilidad y mantenibilidad
  - Facilita la navegación y búsqueda de código
  - Reduce conflictos en control de versiones
  - Mejora la comprensión de responsabilidades (SRP)
  - Acelera el proceso de revisión de código

#### Estructura Recomendada por Directorio:

```
# ❌ EVITAR: Todo en un solo archivo
serializers/
├── __init__.py
└── user_serializers.py  # Contiene 5+ clases

# ✅ PREFERIR: Un archivo por clase
serializers/
├── __init__.py
├── user_serializer.py              # Solo UserSerializer
├── user_create_serializer.py      # Solo UserCreateSerializer
├── user_update_serializer.py      # Solo UserUpdateSerializer
├── change_password_serializer.py  # Solo ChangePasswordSerializer
└── update_email_serializer.py     # Solo UpdateEmailSerializer
```

#### Convenciones de Nombrado:

- **Archivos:** `snake_case` descriptivo que refleje la clase contenida
- **Clases:** `CamelCase` según PEP 8
- **Ejemplo:** 
  - Archivo: `candidate_repository.py`
  - Clase: `CandidateRepository`

#### Exportación en `__init__.py`:

```python
# serializers/__init__.py
from .user_serializer import UserSerializer
from .user_create_serializer import UserCreateSerializer
from .user_update_serializer import UserUpdateSerializer

__all__ = [
    "UserSerializer",
    "UserCreateSerializer",
    "UserUpdateSerializer",
]
```

#### Excepciones a la Regla:

- **Clases muy pequeñas y relacionadas** (ej: Enums, Choices):
  ```python
  # models/choices.py
  class PlanType(models.TextChoices):
      BASIC = "basic", "Básico"
      PRO = "pro", "Pro"
  
  class TenantRole(models.TextChoices):
      ADMIN = "admin", "Administrador"
      MEMBER = "member", "Miembro"
  ```

- **Utilidades compartidas** (ej: helpers, validators):
  ```python
  # utils/validators.py
  def validate_phone(value: str) -> bool:
      ...
  
  def validate_email_domain(value: str) -> bool:
      ...
  ```


---

## 8. Patrones de Implementación

### 8.1. Repositorio Pattern

```python
# apps/recruitment/repositories/candidate_repository.py
from typing import Protocol
from apps.recruitment.models import Candidate

class CandidateRepositoryProtocol(Protocol):
    """Interface para el repositorio de candidatos."""
    
    def get_by_id(self, candidate_id: int) -> Candidate | None:
        """Obtiene un candidato por ID."""
        ...
    
    def filter_by_tenant(self) -> list[Candidate]:
        """Filtra candidatos por tenant."""
        ...

class CandidateRepository:
    """Implementación del repositorio de candidatos."""
    
    def __init__(self, tenant_id: int):
        """
        Inicializa el repositorio con aislamiento de tenant.
        
        Args:
            tenant_id: ID del tenant para aislamiento de datos
        """
        self.tenant_id = tenant_id
    
    def get_by_id(self, candidate_id: int) -> Candidate | None:
        """
        Obtiene un candidato por ID asegurando aislamiento de tenant.
        
        Args:
            candidate_id: ID del candidato
            
        Returns:
            Candidato si existe y pertenece al tenant, None en caso contrario
        """
        return Candidate.objects.filter(
            id=candidate_id,
            tenant_id=self.tenant_id
        ).first()
    
    def filter_by_tenant(self) -> list[Candidate]:
        """
        Filtra todos los candidatos del tenant.
        
        Returns:
            Lista de candidatos del tenant
        """
        return list(Candidate.objects.filter(tenant_id=self.tenant_id))
```

### 8.2. Service Pattern

```python
# apps/recruitment/services/candidate_service.py
from apps.recruitment.repositories.candidate_repository import CandidateRepository
from apps.recruitment.models import Candidate

class CandidateService:
    """Servicio de aplicación para gestión de candidatos."""
    
    def __init__(self, tenant_id: int):
        """
        Inicializa el servicio con el repositorio correspondiente.
        
        Args:
            tenant_id: ID del tenant para aislamiento de datos
        """
        self.repository = CandidateRepository(tenant_id)
    
    def update_candidate_profile(
        self,
        candidate_id: int,
        profile_data: dict
    ) -> Candidate | None:
        """
        Actualiza el perfil de un candidato.
        
        Args:
            candidate_id: ID del candidato
            profile_data: Datos del perfil a actualizar
            
        Returns:
            Candidato actualizado o None si no existe
            
        Raises:
            ValueError: Si los datos del perfil son inválidos
        """
        candidate = self.repository.get_by_id(candidate_id)
        if not candidate:
            return None
        
        # Lógica de negocio aquí
        for key, value in profile_data.items():
            setattr(candidate, key, value)
        
        candidate.save()
        return candidate
```

### 8.3. Adapter Pattern (LLM Provider)

```python
# apps/ai_core/adapters/llm_provider.py
from abc import ABC, abstractmethod
from typing import Protocol

class LLMAdapterProtocol(Protocol):
    """Interface para adaptadores de LLM."""
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        """Genera una completion del LLM."""
        ...

class OpenAIAdapter:
    """Adaptador para OpenAI."""
    
    def __init__(self, api_key: str):
        """
        Inicializa el adaptador de OpenAI.
        
        Args:
            api_key: Clave API de OpenAI
        """
        self.api_key = api_key
        # Inicializar cliente OpenAI
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Genera una completion usando OpenAI.
        
        Args:
            prompt: Prompt para el modelo
            **kwargs: Argumentos adicionales (temperature, max_tokens, etc.)
            
        Returns:
            Texto generado por el modelo
            
        Raises:
            APIError: Si hay un error en la llamada a la API
        """
        # Implementación específica de OpenAI
        pass

class ClaudeAdapter:
    """Adaptador para Anthropic Claude."""
    
    def __init__(self, api_key: str):
        """
        Inicializa el adaptador de Claude.
        
        Args:
            api_key: Clave API de Anthropic
        """
        self.api_key = api_key
        # Inicializar cliente Claude
    
    def generate_completion(self, prompt: str, **kwargs) -> str:
        """
        Genera una completion usando Claude.
        
        Args:
            prompt: Prompt para el modelo
            **kwargs: Argumentos adicionales
            
        Returns:
            Texto generado por el modelo
            
        Raises:
            APIError: Si hay un error en la llamada a la API
        """
        # Implementación específica de Claude
        pass

class LLMProviderService:
    """Servicio que selecciona el adaptador correcto según configuración."""
    
    def __init__(self, tenant_config):
        """
        Inicializa el servicio con la configuración del tenant.
        
        Args:
            tenant_config: Configuración de IA del tenant
        """
        self.tenant_config = tenant_config
    
    def get_adapter(self) -> LLMAdapterProtocol:
        """
        Obtiene el adaptador correcto según la configuración.
        
        Returns:
            Adaptador de LLM configurado
            
        Raises:
            ValueError: Si el proveedor no está soportado
        """
        provider = self.tenant_config.provider
        api_key = self.tenant_config.api_key
        
        if provider == "openai":
            return OpenAIAdapter(api_key)
        elif provider == "claude":
            return ClaudeAdapter(api_key)
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
```

---

## 9. Checklist de Implementación

### Para cada nueva feature:

- [ ] ¿Los modelos están en la capa de Dominio?
- [ ] ¿Existe un Repositorio que abstrae el acceso a datos?
- [ ] ¿El Servicio orquesta la lógica de negocio?
- [ ] ¿Los Adaptadores manejan comunicación externa?
- [ ] ¿Las Vistas solo validan y delegan?
- [ ] ¿Se implementó aislamiento de tenant en repositorios?
- [ ] ¿Las tareas asíncronas están en tasks.py?
- [ ] ¿Se usan Type Hints en todas las funciones?
- [ ] ¿Existen Docstrings en métodos públicos?
- [ ] ¿Las API Keys vienen de variables de entorno?
- [ ] ¿Se maneja correctamente el error handling?
- [ ] ¿Se solicitó confirmación antes de ejecutar comandos destructivos?

---

## 10. Próximos Pasos

1. Crear las apps faltantes: `recruitment` y `ai_core`
2. Implementar los modelos base con tenant_id
3. Configurar Celery y Redis en docker-compose
4. Implementar el middleware de tenant
5. Crear los repositorios base
6. Implementar el sistema de LLM Provider
7. Configurar LangGraph para orquestación de agentes
