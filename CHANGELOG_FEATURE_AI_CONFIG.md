# Documentación de Cambios: Feature AI Config Flow

**Rama:** `feature/implement-ai-config-flow`
**Fecha:** 21/12/2025

Este documento resume los cambios implementados para soportar la configuración de IA por tenant (BYOK - Bring Your Own Key) y la integración en los flujos de reclutamiento y núcleo de IA.

## 1. Apps Impactadas

### 1.1. Tenants (`apps/tenants`)

Se implementó el modelo y la lógica necesaria para que cada tenant pueda configurar su propio proveedor de Inteligencia Artificial.

#### Modelos
*   **`TenantAIConfig` (`models/tenant_ai_config.py`)**: [NUEVO]
    *   Relación `OneToOne` con `Tenant`.
    *   **Campos Clave**:
        *   `provider`: Selección del proveedor (OpenAI, Claude, Gemini).
        *   `api_key`: Llave del API (diseñado para ser encriptado).
        *   `model_name`: Identificador del modelo (ej: `gpt-4`, `claude-3-opus`).
        *   `temperature`: Control de creatividad (0.0 - 2.0).
        *   `max_tokens`: Límite de tokens por respuesta.
    *   **Métodos**:
        *   `get_safe_api_key()`: Retorna versión ofuscada de la llave para UI.
        *   `activate()` / `deactivate()`: Control de estado.

#### Servicios
*   **`TenantAIConfigService` (`services/tenant_ai_config_service.py`)**: [NUEVO]
    *   Lógica de negocio para crear y actualizar configuraciones.
    *   Validaciones de límites (temperatura, tokens).
    *   Manejo transaccional para operaciones de configuración.

#### Vistas (API)
*   **`TenantAIConfigViewSet` (`views/ai_config_views.py`)**: [NUEVO]
    *   `GET /`: Obtiene la configuración actual del tenant.
    *   `POST /`: Crea o actualiza la configuración.
    *   `POST /activate/`: Activa la configuración personalizada.
    *   `POST /deactivate/`: Desactiva la configuración personalizada (volver a default).

#### Serializers
*   **`TenantAIConfigSerializer`**: Para lectura (incluye `safe_api_key`).
*   **`TenantAIConfigCreateSerializer`**: Para escritura (valida input de `api_key`).

---

### 1.2. AI Core (`apps/ai_core`)

Adaptación del núcleo de IA para soportar múltiples proveedores basados en la configuración del tenant.

#### Adapters
*   **`llm_factory.py`**: [MODIFICADO]
    *   Función `get_llm_for_tenant(tenant_config)`:
        *   **Lógica de Selección**:
            1.  Verifica si el tenant tiene configuración activa y API Key (BYOK).
            2.  Si SI: Instancia el cliente del proveedor seleccionado (OpenAI, Anthropic, Google) con la llave del cliente.
            3.  Si NO: Realiza fallback a la configuración global de la plataforma (Llaves maestras).

---

### 1.3. Recruitment (`apps/recruitment`)

Integración de la configuración de IA en el flujo de vacantes.

#### Modelos
*   **`JobVacancy` (`models/job_vacancy.py`)**: [ACTUALIZADO]
    *   Campo **`interview_mode`**:
        *   `AUTO`: Entrevista conducida por Agente de IA.
        *   `MANUAL`: Entrevista tradicional humana.
    *   Esto permite decidir vacante por vacante si se utilizará el stack de IA configurado.

## Resumen Técnico

| Componente | Tipo | Estado | Descripción |
| :--- | :--- | :--- | :--- |
| `TenantAIConfig` | Modelo | Nuevo | Persistencia de config BYOK |
| `TenantAIConfigService` | Servicio | Nuevo | Lógica de negocio y validación |
| `TenantAIConfigViewSet` | Vista | Nuevo | API Endpoints para Frontend |
| `get_llm_for_tenant` | Factory | Actualizado | Router de proveedores LLM |
| `JobVacancy.interview_mode` | Campo | Nuevo | Switch para activar flujo IA |

## Notas de Implementación
1.  **Encriptación**: La estructura para guardar la `api_key` está lista, pero la encriptación real está marcada como TODO en el servicio/modelo.
2.  **Validación**: Se implementaron validadores para `temperature` (0-2) y `max_tokens`.
