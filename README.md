# 🛫 OnTrackIA V1-Core - Aviation Compliance Platform

**Entidad Digital de Confianza para la Aviación Mundial**

[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Compliance](https://img.shields.io/badge/compliance-FAA%20%7C%20EASA%20%7C%20CASA-blue.svg)](docs/regulatory_framework.md)
[![AI Act](https://img.shields.io/badge/EU%20AI%20Act-Compliant-green.svg)](docs/ai_governance.md)
[![GDPR](https://img.shields.io/badge/GDPR-Compliant-green.svg)](docs/privacy.md)

---

## 🎯 Visión

OnTrackIA V1-Core es el **primer sistema de gestión de auditorías aeronáuticas** con:

- ✅ **Integridad Forense SHA-256** - Nivel bancario
- ✅ **Gobernanza IA (EU AI Act)** - Human-in-the-Loop obligatorio
- ✅ **Trazabilidad Total (FAA/EASA/CASA)** - Master Audit Log inmutable
- ✅ **Privacidad GDPR** - Row-Level Security nativo
- ✅ **Adaptabilidad Global** - Multi-territorio (CASA, EASA, FAA, ANAC, Transport Canada)

---

## 🏛️ Certificaciones

| Regulación | Cumplimiento | Componente Técnico |
|------------|--------------|-------------------|
| **EU AI Act (2024/1689)** | ✅ Human-in-the-Loop | `ai_governance.py` |
| **FAA Part 43** | ✅ Audit Trail 7 años | `system_audit_logs` |
| **EASA Part 145** | ✅ Sello Forense SHA-256 | `pdf_export.py` |
| **CASA Australia** | ✅ Trazabilidad Total | Master Audit Log |
| **GDPR** | ✅ RLS + Pseudonimización | `002_enable_rls.sql` |
| **ISO 42001** | ✅ AI Management System | `AIGovernanceService` |
| **ISO 27001** | ✅ Information Security | PostgreSQL RLS |
| **ICAO Annex 19** | ✅ SMS Risk Matrix 5x5 | `sms_service.py` |

---

## 🚀 Características Principales

### 1. **Tridente de Cumplimiento**

- **AUDIT MODULE** - Contextos, Findings, RCA con IA asistida, PDF forense
- **SMS MODULE** - Matriz ICAO 5x5, reportes de seguridad, cálculo automático
- **AI GOVERNANCE** - Mistral LLM con Human-in-the-Loop, transparencia total

### 2. **Caja Negra de Trazabilidad**

Master Audit Log - Registro inmutable de todas las operaciones:

- 📜 **Blockchain-like** - Cada entrada encadena hash de la anterior
- 🔒 **Inmutable** - Triggers PostgreSQL previenen UPDATE/DELETE
- 🔍 **Forense** - IP, User Agent, timestamp UTC, SHA-256

### 3. **Cielos Abiertos - Multi-Territorio**

Sistema adaptable a: 🇦🇺 CASA | 🇪🇺 EASA | 🇺🇸 FAA | 🇬🇧 UK CAA | 🇧🇷 ANAC | 🇨🇦 Transport Canada | 🇺🇾 DINACIA

---

## 📦 Arquitectura

```
backend/
├── api/app/
│   ├── models/          # Audit, SMS, System Audit Log, AI Decision Log
│   ├── services/        # CRUD con RLS, ICAO 5x5, AI Governance, PDF Export
│   ├── routers/         # Audit, SMS, Audit Trail, AI Act APIs
│   └── middleware/      # Audit Logging (captura automática)
├── alembic/versions/    # RLS, Automation Engine, Master Audit Log
└── rag_server_mistral.py  # Main server + RAG

frontend/
└── src/components/      # Glass Cockpit, SMS, Audit Trail Viewer
```

---

## 🔧 Instalación Rápida

```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_database.py
python rag_server_mistral.py

# Frontend
cd frontend
npm install && npm run dev
```

---

## 🌐 Despliegue Producción

Ver [`DEPLOYMENT_CHECKLIST.md`](DEPLOYMENT_CHECKLIST.md)

---

## 📊 API Endpoints

- **Audit:** `/api/v2/audit/contexts`, `/api/v2/audit/findings`, `/api/v2/audit/rca`
- **SMS:** `/api/v2/sms/reports`, `/api/v2/sms/risk-matrix`
- **Audit Trail:** `/api/v2/audit-trail/logs`, `/api/v2/audit-trail/verify-integrity`
- **AI Governance:** `/api/ai-act/systems`, `/api/ai-act/governance/logs`

---

## 📖 Documentación

- [Marco Regulatorio Global](docs/regulatory_framework.md)
- [Guía de Despliegue](DEPLOYMENT_CHECKLIST.md)
- [AI Governance](docs/ai_governance.md)

---

## 📜 Licencia

**Proprietary** - OnTrackIA © 2026

---

**OnTrackIA V1-Core** - *Donde la integridad forense se encuentra con la inteligencia artificial*

🛫 **Despegue Autorizado** 🛫
