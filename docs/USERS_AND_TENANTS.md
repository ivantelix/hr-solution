# Arquitectura de Usuarios y Tenants

## 📋 Modelo de Negocio

Esta plataforma está diseñada para **PYMEs y departamentos de HR** que necesitan gestionar procesos de reclutamiento.

### Concepto Clave

**Todo usuario que se registra en la plataforma se convierte automáticamente en OWNER de un nuevo tenant (empresa).**

```
Usuario Registrado = Tenant Owner
│
├─> Tiene su propia empresa/tenant
├─> Puede invitar empleados de HR
└─> Gestiona su propio equipo de reclutamiento
```

## 🎯 Roles en el Sistema

### 1. **OWNER** (Dueño)
- Usuario que creó el tenant
- Permisos máximos dentro del tenant
- Puede gestionar suscripción y billing
- Puede invitar/eliminar usuarios
- **Se asigna automáticamente al registrarse**

### 2. **ADMIN** (Administrador)
- Puede gestionar usuarios del tenant
- Puede configurar el tenant
- No puede eliminar al OWNER
- Asignado por el OWNER

### 3. **MEMBER** (Miembro)
- Usuario regular del tenant
- Puede usar las funcionalidades de HR
- Permisos limitados de configuración
- Asignado por OWNER o ADMIN

## 🚀 Flujo de Registro

### Registro de Nuevo Tenant Owner

**Endpoint:** `POST /auth/register/`

**Request:**
```json
{
  "username": "admin@empresa.com",
  "email": "admin@empresa.com",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "phone": "+1234567890",
  "company_name": "Mi Empresa S.A.",
  "company_slug": "mi-empresa",
  "industry": "technology",
  "plan": "basic"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "admin@empresa.com",
    "email": "admin@empresa.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "phone": "+1234567890",
    "is_email_verified": false
  },
  "tenant": {
    "id": "uuid-here",
    "name": "Mi Empresa S.A.",
    "slug": "mi-empresa",
    "plan": "basic",
    "is_active": true,
    "max_users": 5
  },
  "tokens": {
    "refresh": "refresh-token-here",
    "access": "access-token-here"
  },
  "message": "Cuenta creada exitosamente. Bienvenido a la plataforma."
}
```

### Lo que sucede automáticamente:

1. ✅ Se crea el **User**
2. ✅ Se crea el **Tenant**
3. ✅ Se crea el **TenantMembership** con rol `OWNER`
4. ✅ Se generan **tokens JWT** para login automático
5. ✅ El usuario puede empezar a usar la plataforma inmediatamente

## 👥 Gestión de Usuarios Adicionales

Una vez registrado, el OWNER puede invitar empleados de HR:

### Invitar Usuario (TODO)

**Endpoint:** `POST /users/invite/`

**Request:**
```json
{
  "email": "reclutador@empresa.com",
  "first_name": "María",
  "last_name": "González",
  "role": "member"
}
```

**Flujo:**
1. Se envía email de invitación
2. El usuario crea su contraseña
3. Se vincula automáticamente al tenant del invitador
4. Recibe el rol asignado

## 🔐 Autenticación

### Login

**Endpoint:** `POST /api/token/`

```json
{
  "username": "admin@empresa.com",
  "password": "SecurePass123"
}
```

### Refresh Token

**Endpoint:** `POST /api/token/refresh/`

```json
{
  "refresh": "refresh-token-here"
}
```

## 📊 Estructura de Datos

```
User (Persona)
├─ username
├─ email
├─ password
├─ first_name
├─ last_name
├─ phone
└─ is_email_verified

Tenant (Empresa)
├─ id (UUID)
├─ name
├─ slug
├─ plan (basic/pro/enterprise)
├─ is_active
├─ max_users
├─ logo
└─ primary_color

TenantMembership (Relación)
├─ tenant (FK)
├─ user (FK)
├─ role (owner/admin/member)
├─ is_active
├─ joined_at
└─ invited_by (FK)
```

## 🔄 Casos de Uso

### 1. Registro de Nueva Empresa
```
Usuario → Registra cuenta → Se convierte en OWNER → Tiene su tenant
```

### 2. Invitación de Empleado
```
OWNER → Invita usuario → Usuario acepta → Se une al tenant como MEMBER
```

### 3. Promoción de Usuario
```
OWNER → Promueve MEMBER → Usuario se convierte en ADMIN
```

### 4. Usuario Multi-Tenant (Futuro)
```
Usuario → Puede ser invitado a múltiples tenants
        → Tiene diferentes roles en cada tenant
```

## 🎨 Endpoints Disponibles

### Públicos (Sin autenticación)
- `POST /auth/register/` - Registro de tenant owner
- `POST /api/token/` - Login
- `POST /api/token/refresh/` - Refresh token

### Autenticados (Requieren token)
- `GET /users/` - Listar usuarios del tenant
- `GET /users/{id}/` - Detalle de usuario
- `PATCH /users/{id}/` - Actualizar usuario
- `DELETE /users/{id}/` - Eliminar usuario
- `POST /users/{id}/change-password/` - Cambiar contraseña
- `POST /users/{id}/update-email/` - Actualizar email

### Tenant Management
- `GET /tenants/` - Listar tenants del usuario
- `GET /tenants/{id}/` - Detalle del tenant
- `PATCH /tenants/{id}/` - Actualizar tenant
- `POST /tenants/{id}/activate/` - Activar tenant
- `POST /tenants/{id}/deactivate/` - Desactivar tenant

## 🔒 Permisos y Seguridad

### Middleware de Tenant Isolation
Todos los queries se filtran automáticamente por el tenant del usuario autenticado.

### Validaciones
- Email único en toda la plataforma
- Username único en toda la plataforma
- Slug de tenant único
- Límite de usuarios por tenant según plan

### Planes y Límites
- **Basic**: 5 usuarios
- **Pro**: 20 usuarios
- **Enterprise**: Ilimitado

## 📝 Próximos Pasos

1. ✅ Implementar sistema de invitaciones
2. ✅ Agregar verificación de email
3. ✅ Implementar recuperación de contraseña
4. ✅ Agregar sistema de permisos granular
5. ✅ Implementar billing y suscripciones
