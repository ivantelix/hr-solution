Documento de Especificación Técnica: SaaS de Reclutamiento Multi-Agente con IA
==============================================================================

1\. Resumen Ejecutivo
---------------------

Desarrollo de una plataforma SaaS multitenant diseñada para automatizar flujos de reclutamiento (Sourcing, Screening, Entrevistas) mediante un sistema multi-agente. La arquitectura prioriza la escalabilidad, el aislamiento de datos por cliente y la independencia tecnológica de los modelos de lenguaje (LLMs).

2\. Stack Tecnológico
---------------------

*   **Backend Framework:** Django 5+ (Python 3.11+).
    
*   **API Framework:** Django Rest Framework (DRF).
    
*   **Base de Datos:** PostgreSQL 15+ (Arquitectura Shared-Database).
    
*   **Tareas Asíncronas:** Celery + Redis (Broker).
    
*   **Orquestación de IA:** LangGraph (para grafos de agentes con estado).
    
*   **Infraestructura:** Docker & Docker Compose.
    
*   **Entorno de Desarrollo:** Windsurf (AI IDE).
    

3\. Arquitectura del Sistema
----------------------------

Se implementa una **Arquitectura Hexagonal (Puertos y Adaptadores)** fusionada con principios de **Domain-Driven Design (DDD)** para desacoplar la lógica de negocio de la infraestructura.

### 3.1. Estructura de Directorios (Modular)

El proyecto evita el patrón monolítico de Django. Se divide en apps que actúan como **Bounded Contexts**.

Plaintext

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   /  ├── core/                   # Configuración del Proyecto (Settings)  │   ├── settings/           # Configuración dividida (base, dev, prod, test)  │   ├── urls.py  │   └── wsgi.py  ├── apps/                   # Bounded Contexts  │   ├── users/              # Gestión de Identidad (Auth)  │   ├── tenants/            # Gestión de SaaS (Clientes, Planes, Memberships)  │   ├── recruitment/        # Lógica de Negocio (Vacantes, Candidatos)  │   └── ai_core/            # Motor Central de IA (Orquestación, LLMs)  ├── docker-compose.yml      # Orquestación de servicios (Web, DB, Worker, Redis)  ├── Dockerfile              # Imagen de la aplicación  └── manage.py   `

### 3.2. Capas de la Aplicación (DDD) dentro de cada App

Cada app (recruitment, ai\_core) sigue esta estructura interna:

*   **models/ (Dominio):** Entidades y lógica de estado puro. No contienen lógica externa.
    
*   **services/ (Aplicación):** Casos de Uso. Orquestan la lógica llamando a Repositorios y Adaptadores.
    
*   **repositories/ (Infraestructura):** Abstracción del ORM. El servicio pide datos al repo, no al modelo directamente.
    
*   **adapters/ (Infraestructura):** Comunicación con el mundo exterior (APIs de OpenAI, LinkedIn, WhatsApp).
    
*   **views/ (Infraestructura):** Capa de presentación (HTTP). Solo valida input y llama a Tareas o Servicios.
    
*   **tasks.py:** Definición de tareas asíncronas para Celery.
    

4\. Estrategia Multitenant
--------------------------

Se utiliza el modelo **Base de Datos Compartida, Esquema Compartido** para eficiencia de costos y mantenimiento.

### 4.1. Aislamiento de Datos

*   **Identificación:** Middleware intercepta el JWT, extrae el tenant\_id y lo inyecta en el request.
    
*   **Persistencia:** Todos los modelos críticos (JobVacancy, Candidate) tienen un campo obligatorio tenant\_id.
    
*   **Repositorios Seguros:** El aislamiento se aplica en la capa de Repositorio. El repositorio requiere el tenant\_id en su constructor y lo aplica automáticamente a todos los filtros .filter(tenant\_id=self.tenant\_id).
    

### 4.2. Modelos Clave (apps/tenants)

*   **Tenant:** Representa a la Pyme/Cliente. Define el plan (Basic, Pro, Enterprise).
    
*   **TenantMembership:** Tabla intermedia que vincula User con Tenant y define el role (Admin, Member).
    

5\. Orquestación de Agentes y IA (apps/ai\_core)
------------------------------------------------

La lógica de IA está centralizada en una app dedicada (ai\_core) para ser reutilizable y agnóstica al negocio de reclutamiento.

### 5.1. Flujo de Ejecución Asíncrono

1.  **Trigger:** Usuario hace POST a la API (recruitment).
    
2.  **Cola:** La vista envía una tarea a **Celery** (tasks.py).
    
3.  **Worker:** Un proceso worker ejecuta la tarea.
    
4.  **Orquestación:** La tarea llama a ai\_core para iniciar un grafo de **LangGraph**.
    
5.  **Ejecución:** Los nodos del grafo (Agentes) ejecutan herramientas y actualizan el estado.
    

### 5.2. Independencia del Modelo (Pattern Provider)

El sistema es agnóstico al LLM (OpenAI, Claude, Llama).

*   **TenantAIConfig:** Modelo donde cada cliente configura su proveedor preferido y API Key (BYOK - Bring Your Own Key).
    
*   **LLMProvider:** Servicio que instantiates el adaptador correcto (OpenAIAdapter, ClaudeAdapter) basado en la configuración del tenant en tiempo de ejecución.
    

### 5.3. Herramientas (Tools)

Los agentes no interactúan con la DB directamente. Usan "Tools" que envuelven a los **Repositorios** y **Adaptadores** del sistema.

6\. Infraestructura y Despliegue (Docker)
-----------------------------------------

El sistema se orquesta mediante docker-compose con tres servicios principales:

1.  **web:** Contenedor Django corriendo con Gunicorn (maneja peticiones HTTP).
    
2.  **celery\_worker:** Contenedor Django corriendo Celery (maneja agentes de IA y tareas pesadas).
    
3.  **db:** Contenedor PostgreSQL 15.
    
4.  **redis:** Contenedor Redis (Broker de mensajes para Celery).