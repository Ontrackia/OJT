# OnTrackIA OJT - On-the-Job Training

## 📋 Descripción

Sistema de gestión de formación práctica (OJT - On-the-Job Training) para técnicos de mantenimiento aeronáutico, cumpliendo con estándares RAC LPTA 66, UK CAA CAP 741, y AAC F1/F2.

---

## 🎯 Framework de Compliance

**OnTrackIA OJT V2.0** es una capa de orquestación unificada que integra:

- **Forensic Integrity**: Sellado SHA-256 de todas las evidencias
- **AI Governance**: "Senior Auditor Coach" basado en ICAO Doc 9859
- **Offline-First PWA**: Operación completa sin conexión vía IndexedDB
- **Branding "Morado Oscuro"**: `#0a051a` + `#7c3aed`
- **Mobile-Optimized UI**: 44px minimum touch targets

---

## 📁 Estructura del Proyecto

```
OnTrackIA_OJT/
├── backend/             # API Backend (FastAPI + SQLAlchemy)
│   └── api/
│       └── app/
│           ├── models/
│           │   └── ojt_models.py      # Modelos de datos OJT
│           └── routers/
│               └── ojt.py             # Endpoints API OJT
├── frontend/            # Frontend (React)
│   └── src/
│       └── pages/
│           └── OJTPage.jsx            # Página principal OJT
├── n8n-workflows/       # Automatizaciones
│   └── 4-notificacion-ojt.json        # Workflow notificaciones
└── docs/                # Documentación
    └── knowledge_item/                # Framework completo de compliance
```

---

## 🗄️ Modelos de Datos

### 1. OJTPerson

Personas en formación OJT

- `full_name`, `position`, `department`
- `supervisor_id` - ID del supervisor
- `status` - active/inactive

### 2. OJTTask

Tareas de formación definidas

- `task_code`, `task_title`, `task_description`
- `task_category` - Categoría (Mechanical, Avionics, etc.)
- `requires_evidence` - Boolean

### 3. OJTPersonTask

Asignaciones de tareas a personas

- `person_id`, `task_id`
- `status` - assigned/in_progress/completed/validated
- `supervisor_validated` - Boolean
- `validated_by`, `validated_at`

### 4. OJTEvidence

Evidencias de cumplimiento

- `evidence_type` - photo/document/video
- `file_path` - MongoDB ID
- `file_hash_sha256` - Integridad forense

---

## 🔌 API Endpoints

### Personas

- `POST /api/ojt/persons` - Crear persona OJT
- `GET /api/ojt/progress/{person_id}` - Ver progreso de persona

### Tareas

- `POST /api/ojt/tasks` - Crear tarea OJT
- `POST /api/ojt/assign` - Asignar tarea a persona

### Evidencias

- `POST /api/ojt/evidences/{person_task_id}` - Subir evidencia

### Validación

- `POST /api/ojt/validate/{person_task_id}` - Validar tarea (supervisor)
- `GET /api/ojt/check-authorization/{person_id}` - Verificar elegibilidad

---

## ⚙️ Estado del Proyecto

> [!WARNING]
> **Este proyecto fue reconstruido manualmente** desde código recuperado tras pérdida de datos.

### ✅ Disponible

- ✅ Modelos de datos completos (4 modelos SQLAlchemy)
- ✅ Router API completo (8 endpoints)
- ✅ Página frontend básica (OJTPage.jsx)
- ✅ Workflow n8n de notificaciones
- ✅ Knowledge Item con framework completo de compliance

### ❌ Faltante (requiere desarrollo)

- ❌ `requirements.txt` - Dependencias Python
- ❌ `package.json` - Dependencias Node.js
- ❌ `docker-compose.yml` - Configuración Docker
- ❌ `.env.example` - Variables de entorno
- ❌ Migraciones de base de datos
- ❌ Tests automatizados
- ❌ Frontend completo (solo página básica)
- ❌ Componentes adicionales de UI
- ❌ Integración completa con backend OnTrackia principal

---

## 🚀 Próximos Pasos

### 1. Recuperar del Servidor (RECOMENDADO)

Si el servidor Hetzner (46.225.79.232) está accesible:

```bash
ssh root@46.225.79.232
scp root@46.225.79.232:/var/www/ontrackia/OnTrackIA_OJT.zip ~/Desktop/
```

### 2. Completar Dependencias

Crear `requirements.txt` y `package.json` basados en ontrackia-platform-v2

### 3. Integración

Integrar este código con el proyecto principal OnTrackia

---

## 📖 Documentación Técnica

Ver `docs/knowledge_item/` para:

- `overview.md` - Framework general
- `implementation/ojt_module.md` - Especificaciones del módulo
- `implementation/forensic_integrity.md` - Sistema SHA-256
- `architecture/pwa_offline.md` - Arquitectura PWA
- `ai/governance_auditor.md` - AI "Senior Auditor Coach"
- `security/hardened_infrastructure.md` - Seguridad
- `ui_ux/branding_standard.md` - Estándares de branding

---

## 📞 Información de Recuperación

**Proyecto recuperado:** 4 de febrero de 2026  
**Fuente:** ontrackia-platform-v2 (recuperado de `.gemini/antigravity/playground`)  
**Servidor producción:** root@46.225.79.232 (actualmente inaccesible)  

---

## ⚖️ Compliance Regulatorio

| Estándar | Cobertura |
|----------|-----------|
| RAC LPTA 66 | 70% Appendix 1 |
| UK CAA CAP 741 | ATA chapter registration |
| AAC F1/F2 | Experience certification |

---

**Nota:** Este README fue generado automáticamente durante el proceso de recuperación. Para versión completa del proyecto, recuperar desde servidor Hetzner.
