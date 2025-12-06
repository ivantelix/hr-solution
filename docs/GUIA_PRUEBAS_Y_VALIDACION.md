# 🧪 Guía de Pruebas y Validación - HR Solution

> **Propósito:** Este documento te ayuda a probar sistemáticamente cada flujo del sistema, entender en qué estado te encuentras, qué funciona correctamente y qué necesita corrección o mejora.

> **Última Actualización:** 2025-12-06

---

## 📋 Índice

1. [Estado Actual del Proyecto](#estado-actual-del-proyecto)
2. [Prerrequisitos para Pruebas](#prerrequisitos-para-pruebas)
3. [Flujos de Prueba Detallados](#flujos-de-prueba-detallados)
4. [Checklist de Validación](#checklist-de-validación)
5. [Problemas Comunes y Soluciones](#problemas-comunes-y-soluciones)
6. [Próximos Pasos Recomendados](#próximos-pasos-recomendados)

---

## 📊 Estado Actual del Proyecto

### ✅ Completado (FASE 1 - 100%)

#### App `users` - Gestión de Usuarios
- ✅ Registro de usuarios
- ✅ Autenticación JWT
- ✅ Actualización de perfil
- ✅ Cambio de contraseña
- ✅ Actualización de email
- ✅ Verificación de email
- ✅ Activación/Desactivación de usuarios

#### App `tenants` - Multitenancy
- ✅ Creación de tenants (empresas)
- ✅ Gestión de membresías
- ✅ Configuración de IA por tenant (BYOK)
- ✅ Middleware de aislamiento de datos
- ✅ Roles (Admin/Member)

### 🚧 En Desarrollo (FASE 2)

#### App `recruitment` - Reclutamiento
- 🚧 Gestión de vacantes
- 🚧 Postulaciones de candidatos
- 🚧 Evaluación de candidatos

#### App `ai_core` - Inteligencia Artificial
- 🚧 Workflows de IA
- 🚧 Agentes conversacionales
- 🚧 Herramientas de LinkedIn
- 🚧 Herramientas de Email

---

## 🔧 Prerrequisitos para Pruebas

### 1. Verificar Entorno de Desarrollo

```bash
# 1. Verificar que la base de datos esté corriendo
docker-compose ps

# Deberías ver el servicio 'db' con estado 'Up'
```

**✅ Qué esperar:**
```
NAME                COMMAND                  SERVICE   STATUS
hr-solution-db-1    "docker-entrypoint.s…"   db        Up
```

**❌ Si falla:**
```bash
# Iniciar la base de datos
docker-compose up -d db
```

---

### 2. Aplicar Migraciones

```bash
# 2. Aplicar migraciones de base de datos
python manage.py migrate
```

**✅ Qué esperar:**
```
Running migrations:
  Applying users.0001_initial... OK
  Applying tenants.0001_initial... OK
  Applying tenants.0002_tenant_ai_config... OK
  Applying recruitment.0001_initial... OK
  ...
```

**❌ Si falla:**
- Error de conexión a DB → Verificar que Docker esté corriendo
- Error de sintaxis en modelos → Revisar archivos en `apps/*/models/`

---

### 3. Iniciar Servidor de Desarrollo

```bash
# 3. Iniciar el servidor Django
python manage.py runserver
```

**✅ Qué esperar:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**❌ Si falla:**
- Puerto 8000 ocupado → Usar `python manage.py runserver 8001`
- Error de importación → Verificar estructura de archivos

---

### 4. Herramientas de Prueba

Necesitarás una de estas herramientas para hacer peticiones HTTP:

- **Postman** (Recomendado) - Interfaz gráfica
- **cURL** - Línea de comandos
- **HTTPie** - Línea de comandos amigable
- **Insomnia** - Alternativa a Postman

**Colección de Postman disponible:**
- Archivo: [`docs/hr_solution_postman_collection.json`](file:///opt/projects/hr-solution/docs/hr_solution_postman_collection.json)
- Importar en Postman para tener todos los endpoints precargados

---

## 🧪 Flujos de Prueba Detallados

### FLUJO 1: Onboarding Completo (Usuario + Tenant)

Este es el flujo fundamental que debe funcionar antes que cualquier otro.

#### 1.1 Registro de Usuario

**Endpoint:**
```http
POST http://localhost:8000/api/users/
Content-Type: application/json
```

**Body:**
```json
{
  "username": "admin_test",
  "email": "admin@testcompany.com",
  "password": "SecurePass123!",
  "first_name": "Admin",
  "last_name": "Test"
}
```

**✅ Respuesta Esperada (201 Created):**
```json
{
  "id": 1,
  "username": "admin_test",
  "email": "admin@testcompany.com",
  "first_name": "Admin",
  "last_name": "Test",
  "is_active": true,
  "is_email_verified": false,
  "created_at": "2025-12-06T13:30:00Z"
}
```

**❌ Errores Comunes:**

| Código | Mensaje | Causa | Solución |
|--------|---------|-------|----------|
| 400 | "username already exists" | Usuario duplicado | Usar otro username |
| 400 | "email already exists" | Email duplicado | Usar otro email |
| 400 | "password too short" | Contraseña débil | Usar contraseña más fuerte |
| 500 | Internal Server Error | Error en el servidor | Revisar logs de Django |

**🔍 Qué validar:**
- [ ] El usuario se crea correctamente
- [ ] El password NO se devuelve en la respuesta
- [ ] `is_active` es `true` por defecto
- [ ] `is_email_verified` es `false` por defecto
- [ ] Se genera un `id` automáticamente

---

#### 1.2 Obtener Token JWT (Login)

**Endpoint:**
```http
POST http://localhost:8000/api/token/
Content-Type: application/json
```

**Body:**
```json
{
  "username": "admin_test",
  "password": "SecurePass123!"
}
```

**✅ Respuesta Esperada (200 OK):**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**❌ Errores Comunes:**

| Código | Mensaje | Causa | Solución |
|--------|---------|-------|----------|
| 401 | "Invalid credentials" | Usuario/contraseña incorrectos | Verificar credenciales |
| 401 | "User is inactive" | Usuario desactivado | Activar usuario en admin |

**🔍 Qué validar:**
- [ ] Se reciben dos tokens: `access` y `refresh`
- [ ] Los tokens son strings largos (JWT)
- [ ] **IMPORTANTE:** Copiar el `access` token para los siguientes pasos

**💡 Tip:** Guardar el token en una variable de entorno de Postman:
```javascript
// En Postman, pestaña "Tests"
pm.environment.set("access_token", pm.response.json().access);
```

---

#### 1.3 Crear Tenant (Empresa)

**Endpoint:**
```http
POST http://localhost:8000/api/tenants/
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Body:**
```json
{
  "name": "Tech Solutions Inc.",
  "slug": "tech-solutions",
  "plan": "pro",
  "max_users": 10
}
```

**✅ Respuesta Esperada (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Tech Solutions Inc.",
  "slug": "tech-solutions",
  "plan": "pro",
  "max_users": 10,
  "is_active": true,
  "created_by": 1,
  "created_at": "2025-12-06T13:35:00Z"
}
```

**❌ Errores Comunes:**

| Código | Mensaje | Causa | Solución |
|--------|---------|-------|----------|
| 401 | "Authentication credentials were not provided" | Falta token | Agregar header Authorization |
| 400 | "slug already exists" | Slug duplicado | Usar otro slug |
| 400 | "Invalid plan" | Plan no válido | Usar: basic, pro, enterprise |

**🔍 Qué validar:**
- [ ] El tenant se crea correctamente
- [ ] Se genera un UUID como `id`
- [ ] El usuario actual se asigna como `created_by`
- [ ] **IMPORTANTE:** Guardar el `id` del tenant (lo necesitarás)
- [ ] Se crea automáticamente una membresía con rol ADMIN para el usuario

**💡 Verificar membresía automática:**
```http
GET http://localhost:8000/api/tenants/
Authorization: Bearer <access_token>
```

Deberías ver el tenant que acabas de crear en la lista.

---

### FLUJO 2: Gestión de Equipo (Membresías)

#### 2.1 Invitar Miembro al Tenant

**Prerrequisito:** Crear un segundo usuario (repetir FLUJO 1.1 con diferentes datos)

**Endpoint:**
```http
POST http://localhost:8000/api/tenants/<tenant_id>/add_member/
Content-Type: application/json
Authorization: Bearer <access_token_admin>
```

**Body:**
```json
{
  "user_id": 2,
  "role": "member"
}
```

**✅ Respuesta Esperada (200 OK):**
```json
{
  "id": 2,
  "tenant": "550e8400-e29b-41d4-a716-446655440000",
  "user": 2,
  "role": "member",
  "is_active": true,
  "joined_at": "2025-12-06T13:40:00Z",
  "invited_by": 1
}
```

**❌ Errores Comunes:**

| Código | Mensaje | Causa | Solución |
|--------|---------|-------|----------|
| 403 | "Permission denied" | No eres admin del tenant | Solo admins pueden invitar |
| 400 | "User already member" | Usuario ya es miembro | Usuario ya está en el tenant |
| 400 | "Max users limit reached" | Límite alcanzado | Aumentar max_users del tenant |

**🔍 Qué validar:**
- [ ] La membresía se crea correctamente
- [ ] El rol es "member"
- [ ] Se registra quién invitó (`invited_by`)
- [ ] El usuario invitado puede ver el tenant en su lista

---

#### 2.2 Listar Tenants del Usuario

**Endpoint:**
```http
GET http://localhost:8000/api/tenants/
Authorization: Bearer <access_token>
```

**✅ Respuesta Esperada (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Tech Solutions Inc.",
    "slug": "tech-solutions",
    "plan": "pro",
    "role": "admin"
  }
]
```

**🔍 Qué validar:**
- [ ] Solo se muestran los tenants donde eres miembro
- [ ] Se incluye tu rol en cada tenant
- [ ] Si no eres miembro de ningún tenant, la lista está vacía

---

### FLUJO 3: Configuración de IA (BYOK)

#### 3.1 Configurar IA para el Tenant

**Endpoint:**
```http
POST http://localhost:8000/api/tenants/<tenant_id>/ai_config/
Content-Type: application/json
Authorization: Bearer <access_token_admin>
```

**Body (OpenAI):**
```json
{
  "provider": "openai",
  "api_key": "sk-proj-xxxxxxxxxxxxx",
  "model_name": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**Body (Claude):**
```json
{
  "provider": "claude",
  "api_key": "sk-ant-xxxxxxxxxxxxx",
  "model_name": "claude-3-opus-20240229",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

**✅ Respuesta Esperada (201 Created):**
```json
{
  "id": 1,
  "tenant": "550e8400-e29b-41d4-a716-446655440000",
  "provider": "openai",
  "api_key": "sk-***************",
  "model_name": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 2000,
  "is_active": true
}
```

**❌ Errores Comunes:**

| Código | Mensaje | Causa | Solución |
|--------|---------|-------|----------|
| 403 | "Permission denied" | No eres admin | Solo admins pueden configurar IA |
| 400 | "Invalid provider" | Proveedor no soportado | Usar: openai, claude, llama |
| 400 | "Config already exists" | Ya existe configuración | Usar PUT para actualizar |

**🔍 Qué validar:**
- [ ] La configuración se crea correctamente
- [ ] El `api_key` se oculta parcialmente en la respuesta (seguridad)
- [ ] Los valores por defecto se aplican si no se especifican
- [ ] Solo admins del tenant pueden crear/modificar

---

### FLUJO 4: Proceso de Reclutamiento

> **⚠️ NOTA:** Este flujo depende de la implementación completa de la app `recruitment`. Verifica primero que los modelos y endpoints estén disponibles.

#### 4.1 Crear Vacante

**Endpoint:**
```http
POST http://localhost:8000/api/recruitment/vacancies/
Content-Type: application/json
Authorization: Bearer <access_token>
```

**Body:**
```json
{
  "title": "Senior Python Developer",
  "description": "Buscamos un desarrollador Python con experiencia en Django y arquitectura DDD.",
  "requirements": "- 5+ años de experiencia en Python\n- Experiencia con Django\n- Conocimientos de DDD y Clean Architecture",
  "location": "Remote",
  "salary_min": 80000,
  "salary_max": 120000,
  "currency": "USD",
  "is_remote": true,
  "interview_mode": "auto"
}
```

**✅ Respuesta Esperada (201 Created):**
```json
{
  "id": 1,
  "tenant": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Senior Python Developer",
  "description": "Buscamos un desarrollador Python...",
  "requirements": "- 5+ años de experiencia...",
  "status": "draft",
  "interview_mode": "auto",
  "location": "Remote",
  "salary_min": 80000.00,
  "salary_max": 120000.00,
  "currency": "USD",
  "is_remote": true,
  "created_by": 1,
  "created_at": "2025-12-06T14:00:00Z"
}
```

**🔍 Qué validar:**
- [ ] La vacante se crea en estado "draft"
- [ ] Se asocia automáticamente al tenant del usuario
- [ ] El usuario actual se registra como `created_by`
- [ ] `interview_mode` puede ser: "manual" o "auto"

---

#### 4.2 Publicar Vacante

**Endpoint:**
```http
POST http://localhost:8000/api/recruitment/vacancies/<vacancy_id>/publish/
Authorization: Bearer <access_token>
```

**✅ Respuesta Esperada (200 OK):**
```json
{
  "id": 1,
  "status": "published",
  "published_at": "2025-12-06T14:05:00Z",
  ...
}
```

**🔍 Qué validar:**
- [ ] El estado cambia de "draft" a "published"
- [ ] Se registra la fecha de publicación
- [ ] **Si `interview_mode` es "auto":** Debería disparar el workflow de IA (verificar logs)

**💡 Verificar trigger de IA:**
```bash
# En los logs del servidor Django, deberías ver:
# "Starting AI workflow for vacancy 1..."
```

---

#### 4.3 Postulación Pública (Sin Autenticación)

**Endpoint:**
```http
POST http://localhost:8000/api/recruitment/applications/
Content-Type: application/json
```

**Body:**
```json
{
  "vacancy_id": 1,
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan.perez@example.com",
  "phone": "+1234567890",
  "linkedin_url": "https://linkedin.com/in/juanperez",
  "resume_url": "https://example.com/resume.pdf",
  "source": "linkedin"
}
```

**✅ Respuesta Esperada (201 Created):**
```json
{
  "id": 1,
  "vacancy": 1,
  "candidate": {
    "id": 1,
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan.perez@example.com"
  },
  "status": "pending",
  "applied_at": "2025-12-06T14:10:00Z",
  "source": "linkedin"
}
```

**🔍 Qué validar:**
- [ ] **NO requiere autenticación** (endpoint público)
- [ ] Si el candidato no existe, se crea automáticamente
- [ ] Si el candidato ya existe (mismo email), se reutiliza
- [ ] La aplicación se crea en estado "pending"
- [ ] Se registra la fuente de la postulación

---

### FLUJO 5: Workflow de IA (Avanzado)

> **⚠️ NOTA:** Este flujo requiere configuración completa de IA y puede no estar totalmente implementado.

#### 5.1 Verificar Configuración de IA

**Checklist previo:**
- [ ] Tenant tiene configuración de IA (`TenantAIConfig`)
- [ ] API Key válida configurada
- [ ] Vacante publicada con `interview_mode: "auto"`

#### 5.2 Monitorear Ejecución del Workflow

**Archivos a revisar:**

1. **Logs de Django:**
```bash
# En la terminal donde corre el servidor
# Buscar mensajes como:
# "Starting sourcing workflow for vacancy 1"
# "LLM Provider: openai"
# "Executing analyst agent..."
```

2. **Base de datos:**
```sql
-- Verificar que se crearon conversaciones
SELECT * FROM ai_core_conversation WHERE vacancy_id = 1;

-- Verificar candidatos encontrados
SELECT * FROM recruitment_candidate WHERE source = 'ai_sourcing';
```

**🔍 Qué validar:**
- [ ] El workflow se inicia automáticamente al publicar
- [ ] Se usa el LLM configurado para el tenant
- [ ] Los agentes se ejecutan en orden (Analyst → Sourcer)
- [ ] Se registran las conversaciones en la BD
- [ ] Se crean candidatos automáticamente (si las herramientas funcionan)

---

## ✅ Checklist de Validación por Módulo

### Módulo: Users

| Funcionalidad | Endpoint | Estado | Notas |
|---------------|----------|--------|-------|
| Registro | POST /api/users/ | ⬜ | Probar con datos válidos |
| Login | POST /api/token/ | ⬜ | Guardar access token |
| Listar usuarios | GET /api/users/ | ⬜ | Requiere autenticación |
| Ver perfil | GET /api/users/{id}/ | ⬜ | Solo tu propio perfil |
| Actualizar perfil | PATCH /api/users/{id}/ | ⬜ | first_name, last_name, phone |
| Cambiar contraseña | POST /api/users/{id}/change_password/ | ⬜ | old_password + new_password |
| Actualizar email | POST /api/users/{id}/update_email/ | ⬜ | Requiere verificación |
| Verificar email | POST /api/users/{id}/verify_email/ | ⬜ | Marca como verificado |
| Desactivar usuario | POST /api/users/{id}/deactivate/ | ⬜ | Soft delete |
| Activar usuario | POST /api/users/{id}/activate/ | ⬜ | Restaurar usuario |

---

### Módulo: Tenants

| Funcionalidad | Endpoint | Estado | Notas |
|---------------|----------|--------|-------|
| Crear tenant | POST /api/tenants/ | ⬜ | Crea membresía admin automáticamente |
| Listar mis tenants | GET /api/tenants/ | ⬜ | Solo donde eres miembro |
| Ver tenant | GET /api/tenants/{id}/ | ⬜ | Requiere ser miembro |
| Actualizar tenant | PATCH /api/tenants/{id}/ | ⬜ | Solo admins |
| Agregar miembro | POST /api/tenants/{id}/add_member/ | ⬜ | Solo admins |
| Remover miembro | POST /api/tenants/{id}/remove_member/ | ⬜ | Solo admins |
| Cambiar rol | POST /api/tenants/{id}/update_role/ | ⬜ | Solo admins |
| Configurar IA | POST /api/tenants/{id}/ai_config/ | ⬜ | BYOK - Solo admins |
| Ver config IA | GET /api/tenants/{id}/ai_config/ | ⬜ | API key oculta |

---

### Módulo: Recruitment

| Funcionalidad | Endpoint | Estado | Notas |
|---------------|----------|--------|-------|
| Crear vacante | POST /api/recruitment/vacancies/ | ⬜ | Requiere tenant activo |
| Listar vacantes | GET /api/recruitment/vacancies/ | ⬜ | Filtradas por tenant |
| Ver vacante | GET /api/recruitment/vacancies/{id}/ | ⬜ | Del mismo tenant |
| Actualizar vacante | PATCH /api/recruitment/vacancies/{id}/ | ⬜ | Solo creador o admin |
| Publicar vacante | POST /api/recruitment/vacancies/{id}/publish/ | ⬜ | Trigger de IA si auto |
| Cerrar vacante | POST /api/recruitment/vacancies/{id}/close/ | ⬜ | Cambia estado a closed |
| Postular | POST /api/recruitment/applications/ | ⬜ | Público - No requiere auth |
| Listar aplicaciones | GET /api/recruitment/applications/ | ⬜ | Por vacante |
| Ver aplicación | GET /api/recruitment/applications/{id}/ | ⬜ | Detalles del candidato |

---

### Módulo: AI Core

| Funcionalidad | Estado | Notas |
|---------------|--------|-------|
| LLM Factory | ⬜ | Instancia OpenAI/Claude según config |
| Workflow Builder | ⬜ | Construye grafo de agentes |
| Analyst Agent | ⬜ | Analiza requisitos de vacante |
| Sourcer Agent | ⬜ | Busca candidatos en LinkedIn |
| LinkedIn Tools | ⬜ | Requiere credenciales de LinkedIn |
| Email Tools | ⬜ | Requiere configuración SMTP |
| Candidate Tools | ⬜ | Crea registros en BD |
| Monitoring | ⬜ | Logs y callbacks |

---

## 🐛 Problemas Comunes y Soluciones

### Problema 1: "Authentication credentials were not provided"

**Causa:** Falta el header de autorización o el token es inválido.

**Solución:**
```http
# Asegúrate de incluir el header en TODAS las peticiones autenticadas
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

### Problema 2: "Tenant not found" o "tenant_id is required"

**Causa:** El middleware de tenant no puede determinar el tenant del usuario.

**Solución:**
1. Verificar que el usuario tenga al menos una membresía activa
2. Si tienes múltiples tenants, el sistema debe saber cuál usar
3. Verificar que `TenantMiddleware` esté configurado en `settings.MIDDLEWARE`

**Implementación actual:**
- El tenant se infiere automáticamente de las membresías del usuario
- Si tienes múltiples tenants, se usa el primero (puede necesitar mejora)

---

### Problema 3: "Max users limit reached"

**Causa:** El tenant alcanzó su límite de usuarios según el plan.

**Solución:**
```http
# Actualizar el límite (solo admin)
PATCH /api/tenants/<tenant_id>/
{
  "max_users": 20
}
```

---

### Problema 4: Workflow de IA no se ejecuta

**Diagnóstico:**
1. Verificar que la vacante tenga `interview_mode: "auto"`
2. Verificar que el tenant tenga configuración de IA
3. Revisar logs de Django para errores
4. Verificar que la API key sea válida

**Solución:**
```bash
# Ver logs en tiempo real
python manage.py runserver

# Buscar mensajes de error relacionados con:
# - "TenantAIConfig.DoesNotExist"
# - "Invalid API key"
# - "LLM provider error"
```

---

### Problema 5: "CORS error" (si usas frontend)

**Causa:** Django no permite peticiones desde el origen del frontend.

**Solución:**
```python
# En settings.py
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React
    "http://localhost:5173",  # Vite
]
```

---

## 🎯 Próximos Pasos Recomendados

### Corto Plazo (Esta Semana)

1. **Validar FASE 1 completa:**
   - [ ] Probar todos los endpoints de `users`
   - [ ] Probar todos los endpoints de `tenants`
   - [ ] Verificar que el middleware de tenant funciona
   - [ ] Confirmar que BYOK funciona con al menos un proveedor

2. **Documentar hallazgos:**
   - [ ] Crear lista de bugs encontrados
   - [ ] Documentar comportamientos inesperados
   - [ ] Anotar mejoras necesarias

---

### Mediano Plazo (Próximas 2 Semanas)

3. **Completar FASE 2.1 (Recruitment):**
   - [ ] Implementar todos los endpoints de vacantes
   - [ ] Implementar sistema de postulaciones
   - [ ] Crear flujo completo de candidatos
   - [ ] Probar integración con IA

4. **Completar FASE 2.2 (AI Core):**
   - [ ] Implementar workflow completo
   - [ ] Configurar herramientas de LinkedIn (o mocks)
   - [ ] Configurar herramientas de Email
   - [ ] Probar ejecución end-to-end del workflow

---

### Largo Plazo (Próximo Mes)

5. **Testing Automatizado:**
   - [ ] Crear tests unitarios para services
   - [ ] Crear tests de integración para flujos completos
   - [ ] Configurar CI/CD
   - [ ] Alcanzar 80%+ de cobertura

6. **Optimización y Mejoras:**
   - [ ] Implementar caché (Redis)
   - [ ] Optimizar queries de BD
   - [ ] Implementar rate limiting
   - [ ] Mejorar manejo de errores

---

## 📝 Plantilla de Reporte de Pruebas

Usa esta plantilla para documentar tus pruebas:

```markdown
### Prueba: [Nombre del Flujo]
**Fecha:** 2025-12-06
**Probado por:** [Tu nombre]

#### Configuración:
- Entorno: Development
- Base de datos: PostgreSQL (Docker)
- Python: 3.10+
- Django: 4.2+

#### Pasos Ejecutados:
1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

#### Resultado:
- ✅ Exitoso / ❌ Fallido

#### Observaciones:
- [Comportamiento observado]
- [Diferencias con lo esperado]

#### Bugs Encontrados:
- [Bug 1: Descripción]
- [Bug 2: Descripción]

#### Próximos Pasos:
- [Acción 1]
- [Acción 2]
```

---

## 📚 Referencias Útiles

### Documentación del Proyecto

- [Flujo de Peticiones de IA](file:///opt/projects/hr-solution/docs/flujo_peticiones_ia.md) - Diagrama completo del flujo de IA
- [System Flow and Testing](file:///opt/projects/hr-solution/docs/SYSTEM_FLOW_AND_TESTING.md) - Guía básica de flujos
- [Progress](file:///opt/projects/hr-solution/docs/PROGRESS.md) - Estado de implementación
- [Technical Specifications](file:///opt/projects/hr-solution/docs/technical_specifications.md) - Especificaciones técnicas

### Archivos Clave

- [User Views](file:///opt/projects/hr-solution/apps/users/views/user_views.py) - Endpoints de usuarios
- [Tenant Models](file:///opt/projects/hr-solution/apps/tenants/models/) - Modelos de tenant
- [AI Core Services](file:///opt/projects/hr-solution/apps/ai_core/services/) - Servicios de IA

---

## 💡 Tips Finales

1. **Prueba en orden:** Sigue los flujos en el orden presentado. Cada flujo depende del anterior.

2. **Guarda los IDs:** Anota los IDs de usuarios, tenants y vacantes que crees. Los necesitarás para pruebas posteriores.

3. **Usa Postman Collections:** Importa la colección para tener todos los endpoints listos.

4. **Revisa los logs:** Siempre mantén visible la terminal donde corre Django para ver errores en tiempo real.

5. **Prueba casos límite:** No solo pruebes el "happy path". Intenta:
   - Datos inválidos
   - Usuarios sin permisos
   - Límites alcanzados
   - Campos opcionales vacíos

6. **Documenta todo:** Cada bug que encuentres, cada comportamiento inesperado, cada mejora que identifiques.

---

**¿Necesitas ayuda?**
- Revisa los logs de Django
- Consulta la documentación técnica
- Verifica que todas las migraciones estén aplicadas
- Asegúrate de que el entorno esté correctamente configurado

**¡Buena suerte con las pruebas! 🚀**
