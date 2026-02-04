# Sistema de Vigilancia Normativa Global V2.0

## OnTrackIA OJT - Active Regulation Surveillance

---

## 📋 Visión General

El **Sistema de Vigilancia Normativa Global** es una infraestructura automatizada de monitoreo que asegura que OnTrackIA OJT V2.0 mantenga siempre la base de conocimiento regulatoria más actualizada del sector aeronáutico.

### Componentes Principales

1. **GlobalComplianceMap** (Frontend)
2. **RegulationWatcherService** (Backend)
3. **WatcherScheduler** (Automatización)
4. **RAG Endpoints** (API)

---

## 🗺️ Global Compliance Map

### Descripción

Mapa interactivo que visualiza en tiempo real la cobertura normativa mundial de OnTrackIA.

### Features

- ✅ **Mapa vectorial** con react-simple-maps
- ✅ **Países iluminados** (#7c3aed) según normativas cargadas
- ✅ **Alertas visuales** (parpadeo) para actualizaciones pendientes
- ✅ **Panel lateral** con detalles por región
- ✅ **Filtros** por autoridad (EASA, FAA, CAA, RAC, ICAO)
- ✅ **Soporte bilingüe** ES/EN
- ✅ **Compatible PWA** offline con Dexie.js

### Mapeo de Regiones

```javascript
COUNTRY_MAPPING = {
  'EU': ['DEU', 'FRA', 'ESP', 'ITA', 'POL'],  // EASA
  'US': ['USA'],                               // FAA
  'GB': ['GBR'],                               // UK CAA
  'CO': ['COL'],                               // RAC Colombia
  'MX': ['MEX'],                               // DGAC México
  'PA': ['PAN'],                               // AAC Panamá
  'AE': ['ARE'],                               // GCAA UAE
  'SA': ['SAU'],                               // GACA Saudi
  'ICAO': 'global'                             // Internacional
}
```

### Uso

```jsx
import GlobalComplianceMap from './components/GlobalComplianceMap';

function AdminDashboard() {
  return (
    <GlobalComplianceMap />
  );
}
```

---

## 🔍 Regulation Watcher Service

### Descripción

Servicio backend de monitoreo automático que detecta cambios en las normativas oficiales mediante el seguimiento de hashes SHA-256.

### Workflow

```
1. Fetch URL official → Calculate SHA-256 hash
2. Compare con hash anterior
3. Si cambió → Generar RegulationUpdate
4. Guardar en regulation_updates.json
5. Alerta en mapa (pending updates)
6. Admin aprueba → Re-indexar en ChromaDB
```

### Fuentes Monitoreadas

#### Europa (EASA)

- **Part-66**: Licencias de Personal Técnico
- **Part-145**: Organizaciones de Mantenimiento
- **AMC/GM**: Medios Aceptables de Cumplimiento

#### USA (FAA)

- **Order 8900.1**: Flight Standards Manual
- **AC 65-30**: AMT Logbook
- **14 CFR Part 65**: Certificación de Personal

#### Reino Unido (UK CAA)

- **CAP 741**: Aircraft Maintenance Engineers Logbook

#### Latinoamérica

- **RAC LPTA 66** (Colombia): Licencias Personal Técnico
- **LAR 66** (México): Regulación Regional
- **DGAC** (Panamá): Autoridad de Aviación Civil

#### Internacional (ICAO)

- **Doc 9859**: Safety Management Manual
- **Doc 7192**: Training Manual

### Ejecución Manual

```bash
# Ejecutar vigilancia manual
cd backend/scripts
python regulation_watcher.py
```

### Salida Ejemplo

```
🔍 Checking: Part-66 (EASA)
   ✓ No changes

🔍 Checking: LPTA 66 (RAC Colombia)
   🚨 CAMBIO DETECTADO!
      Old hash: a3f5d8e9c1b2...
      New hash: f7c4a9d2e8b1...
```

---

## ⏰ Watcher Scheduler

### Descripción

Programador de tareas que ejecuta el watcher semanalmente sin intervención manual.

### Configuración

**Frecuencia**: Lunes a las 03:00 AM  
**Delay entre requests**: 2 segundos  
**Timeout por request**: 30 segundos

### Ejecución

```bash
# Iniciar scheduler (modo daemon)
cd backend/scripts
python watcher_scheduler.py &

# Logs
tail -f /var/log/ontrackia/watcher.log
```

### Systemd Service (Producción)

Crear `/etc/systemd/system/ontrackia-watcher.service`:

```ini
[Unit]
Description=OnTrackIA Regulation Watcher
After=network.target

[Service]
Type=simple
User=ontrackia
WorkingDirectory=/opt/ontrackia/backend/scripts
ExecStart=/usr/bin/python3 watcher_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activar:

```bash
sudo systemctl enable ontrackia-watcher
sudo systemctl start ontrackia-watcher
sudo systemctl status ontrackia-watcher
```

---

## 🌐 API Endpoints

### GET `/api/rag/coverage`

Obtiene cobertura normativa global.

**Response**:

```json
{
  "coverage": {
    "EU": {
      "authority": "EASA",
      "documents": 2,
      "regulations": [
        {
          "document_code": "Part-66",
          "language": "en",
          "update_date": "2026-02-04"
        }
      ]
    }
  }
}
```

### GET `/api/rag/pending-updates`

Obtiene actualizaciones pendientes de aprobación.

**Response**:

```json
{
  "updates": [
    {
      "id": "rac_lpta66_1738656000",
      "authority": "RAC Colombia",
      "region": "CO",
      "document_code": "LPTA 66",
      "detected_at": "2026-02-04T03:00:15",
      "change_summary": "La Enmienda 5 añade 3 nuevas tareas en aviónica",
      "status": "pending"
    }
  ]
}
```

### POST `/api/rag/approve-update/{update_id}`

Aprueba una actualización para indexación.

**Response**:

```json
{
  "status": "approved",
  "update_id": "rac_lpta66_1738656000",
  "message": "Update approved and ready for indexing"
}
```

---

## 🎨 UI/UX Guidelines

### Diseño

- ❌ **Prohibido**: Emojis
- ✅ **Obligatorio**: Iconos Lucide (Globe, FileSearch, BellRing, History)
- ✅ **Branding**: Deep Purple (#0a051a) + Glassmorphism
- ✅ **Ergonomía**: Botones 44x44px

### Animaciones

```css
/* Parpadeo de país con actualización */
@keyframes blink-border {
  0%, 100% { stroke: var(--warning); stroke-width: 2; }
  50% { stroke: transparent; stroke-width: 2; }
}

.country-updating {
  animation: blink-border 2s infinite;
}
```

---

## 🔐 Seguridad & Performance

### Rate Limiting

- ✅ Delay de **2 segundos** entre requests
- ✅ Timeout de **30 segundos** por URL
- ✅ User-Agent identificado: `OnTrackIA-RegulationWatcher/2.0`

### Ancho de Banda

**Estimación semanal**:

- 9 fuentes × 1MB promedio por PDF × 1 check/semana = **~9MB/semana**
- Impacto despreciable en servidor Hetzner

### Error Handling

```python
try:
    current_hash = await self.fetch_url_hash(watch.url)
except aiohttp.ClientError:
    # Retry con exponential backoff
    await asyncio.sleep(2 ** retry_count)
```

---

## 📊 Métricas & Monitoring

### KPIs

| Métrica | Target | Actual |
|---------|--------|--------|
| Uptime del Watcher | 99.5% | - |
| Tiempo de detección de cambio | < 7 días | 7 días |
| False positives | < 5% | - |
| Normativas monitoreadas | 20+ | 9 |

### Logs

```python
# Formato de logs
{
  "timestamp": "2026-02-04T03:00:15Z",
  "event": "change_detected",
  "authority": "RAC Colombia",
  "document": "LPTA 66",
  "old_hash": "a3f5...",
  "new_hash": "f7c4..."
}
```

---

## 🚀 Roadmap

### Fase 1 (Actual)

- ✅ Monitoreo básico de 9 fuentes
- ✅ Mapa global de cobertura
- ✅ Alertas visuales

### Fase 2 (Q2 2026)

- ⏳ Diff inteligente con IA (Mistral)
- ⏳ Notificaciones por email
- ⏳ Dashboard de métricas

### Fase 3 (Q3 2026)

- ⏳ Expansión a 30+ fuentes
- ⏳ Auto-indexación con aprobación automática
- ⏳ Predicción de actualizaciones (ML)

---

## 🛠️ Troubleshooting

### El watcher no detecta cambios

1. Verificar conectividad a internet
2. Revisar logs: `tail -f /var/log/ontrackia/watcher.log`
3. Ejecutar manualmente: `python regulation_watcher.py`
4. Verificar hashes guardados en `config/regulation_watches.json`

### País no se ilumina en el mapa

1. Verificar archivo .md en `docs/knowledge_item/world_regs/`
2. Confirmar que el header tiene metadata correcta:

```markdown
**Autoridad:** EASA
**Código:** Part-66
**Región:** EU
```

3. Re-cargar endpoint `/api/rag/coverage`

### Actualización pendiente no aparece

1. Verificar `data/regulation_updates.json`
2. Confirmar que `status: "pending"`
3. Recargar endpoint `/api/rag/pending-updates`

---

## 📚 Referencias

- [EASA Regulations](https://www.easa.europa.eu/regulations)
- [FAA Orders & Notices](https://www.faa.gov/regulations_policies)
- [UK CAA Publications](https://publicapps.caa.co.uk)
- [RAC Colombia](https://www.aerocivil.gov.co)
- [ICAO Documents](https://www.icao.int/safety)

---

## 👥 Equipo

**Desarrollo**: OnTrackia Dev Team  
**Fecha**: 2026-02-04  
**Versión**: 2.0 Ultimate

---

## 📄 Licencia

Propietaria - OnTrackIA © 2026
