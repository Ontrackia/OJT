# OnTrackIA OJT V2.0 - Protocolo Búnker

## 🔐 Infraestructura de Seguridad Forense Máxima

Este documento describe la implementación completa del **Protocolo Búnker** para OnTrackIA OJT V2.0, garantizando integridad forense, compliance aeronáutico y gobernanza AI.

---

## 📋 Componentes Implementados

### 1. `.env.example` - Configuración Segura ✅

**Ubicación:** `/OnTrackIA_OJT/.env.example`

**Características:**

- 🔑 JWT con HS256 y rotación obligatoria cada 90 días
- 🗄️ PostgreSQL para tablas OJT (integridad referencial)
- 📁 MongoDB para evidencias con sellado SHA-256
- 🤖 Mistral AI para "Senior Auditor Coach" (ICAO Doc 9859)
- 🎨 Branding Morado Oscuro (`#7c3aed` + `#0a051a`)
- 📱 PWA Offline-First con IndexedDB (Dexie.js)
- 📊 Configuración de compliance (RAC LPTA 66, CAP 741)

**Variables Críticas:**

```bash
JWT_SECRET_KEY=CAMBIAR_ESTE_SECRET_MINIMO_64_CARACTERES
MISTRAL_API_KEY=tu_api_key_mistral_aqui
FORENSIC_SEAL_REQUIRED=true
COMPLIANCE_STANDARD=RAC_LPTA_66
```

---

### 2. `docker-compose.yml` - Orquestación Completa ✅

**Ubicación:** `/OnTrackIA_OJT/docker-compose.yml`

**Servicios:**

1. **PostgreSQL 15** - Base de datos principal
2. **MongoDB 7** - Persistencia de evidencias forenses
3. **Backend FastAPI** - API con validación AI
4. **Frontend Vite** - PWA con branding oficial
5. **Redis** (opcional) - Cache y rate limiting

**Características Búnker:**

- ✅ Volúmenes persistentes en `./data/` (no se pierden datos)
- ✅ Healthchecks en todos los servicios
- ✅ Network isolation (`ojt_network`)
- ✅ Auto-restart (`unless-stopped`)
- ✅ Migraciones automáticas en startup

**Comandos:**

```bash
# Levantar infraestructura
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Verificar AI Governance
docker-compose exec backend python verify_ai.py --full-check

# Backup PostgreSQL
docker-compose exec postgres pg_dump -U ontrackia_ojt > backup.sql
```

---

### 3. `verify_ai.py` - Auditoría de Gobernanza AI ✅

**Ubicación:** `/OnTrackIA_OJT/backend/verify_ai.py`

**4 Pilares de Gobernanza:**

#### Pilar 1: Profundidad Técnica (Score >= 7/10)

- Uso de terminología aeronáutica (ATA, AMM, FAA, EASA)
- Referencias a normativa específica
- Estructura lógica con ejemplos concretos

#### Pilar 2: No Superficialidad (>= 200 palabras)

- Respuestas detalladas con contexto
- Evita respuestas genéricas tipo "ChatGPT"

#### Pilar 3: Dirty Dozen (Factores Humanos)

- Mención de: fatiga, complacencia, presión, distracción
- Falta de conocimiento, trabajo en equipo, recursos
- Estrés, conciencia situacional, normas

#### Pilar 4: Trazabilidad

- Referencias a documentos: RAC-145, EASA Part-145, ICAO Doc 9859
- Menciones de ATA chapters, AMM sections

**Uso:**

```bash
python verify_ai.py --check-governance
```

**Salida:**

```
📊 REPORTE DE AUDITORÍA AI GOVERNANCE
======================================
✅ Estado: APROBADO
📈 Profundidad Técnica: 8/10
📝 Palabras: 342
🔗 Trazabilidad: ✓
👥 Dirty Dozen Mencionados: 5
```

---

### 4. `zero_insurrections.py` - Filtro de Nomenclatura ✅

**Ubicación:** `/OnTrackIA_OJT/backend/zero_insurrections.py`

**Términos Prohibidos:**

- ❌ `master` → ✅ `main`
- ❌ `gold` → ✅ `stable`
- ❌ `beta` → ✅ `verified`
- ❌ `alpha` → ✅ `verified`
- ❌ `dev-unstable` → ✅ `development`
- ❌ `experimental` → ✅ `development`

**Severidades:**

- 🔴 **High:** En branches, git, deploy, producción
- 🟡 **Medium:** En comentarios y documentación
- ⚪ **Low:** Otros contextos

**Uso:**

```bash
# Auditar proyecto
python zero_insurrections.py --path . --strict

# Generar script de corrección automática
python zero_insurrections.py --path . --fix
./fix_nomenclature.sh
```

---

### 5. `requirements.txt` - Dependencias Backend ✅

**Ubicación:** `/OnTrackIA_OJT/backend/requirements.txt`

**Dependencias Clave:**

- **Core:** FastAPI 0.109.2, Uvicorn 0.27.1
- **DB:** SQLAlchemy 2.0.25, PyMongo 4.6.1, Alembic 1.13.1
- **Seguridad:** python-jose, bcrypt, cryptography 42.0.2
- **AI:** mistralai 0.1.4, anthropic 0.18.1
- **Forensic:** hashlib (built-in para SHA-256)
- **Monitoring:** Sentry, Prometheus
- **Testing:** pytest, pytest-asyncio, pytest-cov

**Instalación:**

```bash
pip install -r requirements.txt
```

---

### 6. `package.json` - Dependencias Frontend ✅

**Ubicación:** `/OnTrackIA_OJT/frontend/package.json`

**Dependencias Clave:**

- **Core:** React 18.2.0, Vite 5.1.0
- **Offline-First:** Dexie 3.2.4, dexie-react-hooks
- **PWA:** vite-plugin-pwa 0.17.5, workbox-window 7.0.0
- **UI:** lucide-react 0.316.0

**Configuración PWA:**

```json
{
  "theme_color": "#7c3aed",
  "background_color": "#0a051a",
  "display": "standalone",
  "touch_target_min": "44px"
}
```

**Instalación:**

```bash
cd frontend
npm install
npm run dev
```

---

## 🎨 Branding Oficial "Morado Oscuro"

### Paleta de Colores Certificada

| Elemento | Color | Uso |
|----------|-------|-----|
| **Primary** | `#7c3aed` | Botones, enlaces, highlights |
| **Background Deep** | `#0a051a` | Fondo principal |
| **Touch Target** | 44px mínimo | Botones y controles táctiles |
| **Glassmorphism** | Habilitado | Efectos de vidrio esmerilado |

### Variables CSS

```css
:root {
  --primary: #7c3aed;
  --bg-deep: #0a051a;
  --touch-min: 44px;
}
```

---

## 📊 Compliance Aeronáutico

### Estándares Soportados

| Estándar | Cobertura | Validación |
|----------|-----------|------------|
| **RAC LPTA 66** | 70% Appendix 1 | Forensic seal + AI audit |
| **UK CAA CAP 741** | ATA chapters | Task registration |
| **AAC F1/F2** | Experience cert | Evidence validation |
| **ICAO Doc 9859** | SMS framework | AI Senior Auditor |

---

## 🔒 Características de Seguridad

### Forensic Integrity

- ✅ SHA-256 para todas las evidencias
- ✅ Inmutabilidad de registros
- ✅ Audit logs completos
- ✅ Timestamps UTC con precisión de milisegundos

### Autenticación Búnker

- ✅ JWT con rotación obligatoria (90 días)
- ✅ Passwords bcrypt con salt
- ✅ Rate limiting (60 req/min)
- ✅ Session cookies secure + httponly + samesite

### Persistencia Forense

- ✅ PostgreSQL con ACID compliance
- ✅ MongoDB con replicación
- ✅ Backups automáticos configurables
- ✅ Volúmenes Docker persistentes

---

## 📱 PWA Offline-First

### Arquitectura

1. **IndexedDB (Dexie.js)** - Base de datos local
2. **Service Worker (Workbox)** - Cache y sync
3. **SyncEngine** - Sincronización inteligente cada 30s
4. **Conflict Resolution** - Last-write-wins

### Capacidades Offline

- ✅ Consulta de tareas OJT
- ✅ Visualización de progreso
- ✅ Captura de evidencias (fotos)
- ✅ Sincronización automática al reconectar

---

## 🚀 Deployment

### Checklist de Producción

- [ ] Cambiar `JWT_SECRET_KEY` (usar `openssl rand -hex 64`)
- [ ] Configurar passwords de PostgreSQL (32+ caracteres)
- [ ] Configurar password de MongoDB (32+ caracteres)
- [ ] Agregar `MISTRAL_API_KEY` válida
- [ ] Configurar `CORS_ORIGINS` solo con dominios autorizados
- [ ] Habilitar SSL/TLS en todas las conexiones
- [ ] Configurar Sentry DSN para monitoring
- [ ] Ejecutar `verify_ai.py --full-check`
- [ ] Ejecutar `zero_insurrections.py --strict`
- [ ] Configurar backups automáticos (cron)
- [ ] Habilitar Prometheus para métricas

### Comandos de Deployment

```bash
# 1. Clonar repositorio
git clone https://github.com/Ontrackia/OJT.git
cd OJT

# 2. Copiar y configurar .env
cp .env.example .env
nano .env  # Editar secretos

# 3. Crear directorios de persistencia
mkdir -p data/{postgres,mongo,uploads}

# 4. Levantar infraestructura
docker-compose up -d

# 5. Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# 6. Verificar servicios
docker-compose ps
docker-compose logs -f
```

---

## 🧪 Testing

### Tests de Gobernanza

```bash
# Verificar AI governance
docker-compose exec backend python verify_ai.py --full-check

# Verificar nomenclatura
docker-compose exec backend python zero_insurrections.py --strict

# Tests unitarios
docker-compose exec backend pytest

# Tests con cobertura
docker-compose exec backend pytest --cov=app --cov-report=html
```

---

## 📈 Monitoring

### Métricas Clave

- **Uptime del sistema**
- **Tiempo de respuesta API** (p50, p95, p99)
- **Tasa de errores** (<0.1%)
- **AI Governance score** (>= 7/10)
- **Violaciones Zero Insurrections** (= 0)
- **Sync latency PWA** (<5s)

---

## 🎯 Resultado Final

**Protocolo Búnker Implementado:**

- ✅ Seguridad forense máxima (SHA-256 + JWT)
- ✅ Dockerización completa con persistencia
- ✅ AI Governance validada (4 Pilares)
- ✅ Nomenclatura oficial (Zero Insurrections)
- ✅ PWA Offline-First (Dexie.js)
- ✅ Branding Morado Oscuro certificado
- ✅ Compliance aeronáutico (RAC/EASA/AAC)

**Sistema listo para auditoría por autoridad aeronáutica (EASA/RAC).**

---

**Última actualización:** 2026-02-04  
**Versión:** 2.0.0  
**Status:** PRODUCTION-READY ✅
