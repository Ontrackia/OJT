# OnTrackIA OJT V2.0 - Deployment Automation Guide
## Configuración de CI/CD con GitHub Actions

---

## 📋 Resumen

Sistema completo de deployment automático que:
- ✅ Deploy automático en cada push a `main`
- ✅ Migraciones de BD automáticas
- ✅ Auto-indexación de knowledge items en RAG
- ✅ SSH hardening (Protocolo Búnker)
- ✅ Health checks post-deployment
- ✅ Zero downtime deployment

---

## 🚀 Setup Inicial del Servidor

### 1. Ejecutar Script de Setup

En el servidor Hetzner:

```bash
# Descargar el script
curl -O https://raw.githubusercontent.com/Ontrackia/OJT/main/scripts/server_setup.sh

# Hacer ejecutable
chmod +x server_setup.sh

# Ejecutar
sudo ./server_setup.sh
```

El script configurará automáticamente:
- ✅ Usuario `ontrackia`
- ✅ SSH solo con llave pública (sin contraseñas)
- ✅ Firewall UFW
- ✅ Fail2Ban
- ✅ PostgreSQL
- ✅ Nginx
- ✅ Servicios systemd
- ✅ Repositorio Git clonado

### 2. Agregar Llave SSH

**ANTES** del reinicio de SSH:

```bash
# En tu máquina local, generar llave si no existe
ssh-keygen -t ed25519 -C "ontrackia@deployment"

# Copiar llave pública al servidor
cat ~/.ssh/id_ed25519.pub | ssh root@YOUR_SERVER_IP \
  "sudo -u ontrackia tee -a /home/ontrackia/.ssh/authorized_keys"
```

### 3. Verificar Acceso SSH

```bash
# Probar acceso con llave
ssh -i ~/.ssh/id_ed25519 ontrackia@YOUR_SERVER_IP

# Si funciona, continuar con setup
```

---

## 🔐 Configurar GitHub Secrets

En tu repositorio GitHub: **Settings → Secrets and variables → Actions**

Agregar los siguientes secrets:

| Secret Name | Value | Descripción |
|-------------|-------|-------------|
| `HETZNER_HOST` | `123.456.789.0` | IP del servidor |
| `HETZNER_USER` | `ontrackia` | Usuario SSH |
| `HETZNER_SSH_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Llave privada completa |

### Obtener Llave Privada

```bash
cat ~/.ssh/id_ed25519
```

Copiar **TODO** el contenido (incluido `-----BEGIN` y `-----END`)

---

## 🤖 GitHub Actions Workflow

El archivo `.github/workflows/deploy.yml` se ejecuta automáticamente en cada push a `main`.

### Flujo de Deployment

```
1. Trigger: Push a main
2. GitHub Actions:
   - Checkout código
   - Setup SSH
3. Servidor Hetzner:
   - Git pull
   - Instalar dependencias backend
   - Aplicar migraciones BD
   - Auto-indexar knowledge items
   - Restart backend service
   - Build frontend
   - Deploy a nginx
   - Health check
4. Notificación: Success/Failure
```

### Deployment Manual

Si necesitas deployar manualmente:

```bash
# En GitHub: Actions → Deploy to Hetzner → Run workflow
```

---

## 🗄️ Migraciones de Base de Datos

### Cómo Funciona

El script `apply_migrations.py` automáticamente:
1. Busca archivos SQL en `/backend/database/migrations/`
2. Calcula hash SHA-256 de cada archivo
3. Compara con tabla `_migrations`
4. Aplica solo las nuevas o modificadas
5. Registra en tabla de control

### Crear Nueva Migración

```bash
cd backend/database/migrations

# Crear archivo con timestamp
touch $(date +%Y%m%d%H%M%S)_add_feature_x.sql
```

Ejemplo: `20260204103000_add_feature_x.sql`

```sql
-- Add new feature X
ALTER TABLE ojt_tasks 
ADD COLUMN new_field VARCHAR(255);

-- Create index
CREATE INDEX idx_task_new_field ON ojt_tasks(new_field);
```

### Verificar Migraciones

```bash
# En el servidor
cd /opt/ontrackia/OJT/backend
source venv/bin/activate
python scripts/apply_migrations.py
```

---

## 🧠 Auto-Indexación RAG

### Cómo Funciona

El script `auto_index_knowledge.py`:
1. Busca archivos `.md` en `/docs/knowledge_item/`
2. Calcula hash SHA-256
3. Compara con `data/index_log.json`
4. Indexa solo archivos nuevos/modificados en ChromaDB
5. Actualiza log

### Agregar Nuevo Conocimiento

```bash
# Agregar archivo .md a:
/docs/knowledge_item/world_regs/NEW_REGULATION.md

# El próximo push a main lo indexará automáticamente
git add docs/knowledge_item/world_regs/NEW_REGULATION.md
git commit -m "feat: add NEW_REGULATION normative"
git push origin main
```

### Verificar Indexación

```bash
# En el servidor
cd /opt/ontrackia/OJT/backend
source venv/bin/activate
python scripts/auto_index_knowledge.py
```

---

## 🛡️ SSH Hardening (Protocolo Búnker)

### Configuración Aplicada

```ini
# Solo llave pública
PasswordAuthentication no
PubkeyAuthentication yes

# Sin root
PermitRootLogin no

# Solo usuario ontrackia
AllowUsers ontrackia

# Algoritmos seguros
KexAlgorithms curve25519-sha256
Ciphers chacha20-poly1305@openssh.com
MACs hmac-sha2-512-etm@openssh.com
```

### Fail2Ban

Protección contra ataques de fuerza bruta:
- **3 intentos** fallidos → Ban **1 hora**
- Logs en `/var/log/fail2ban.log`

### Firewall UFW

Puertos abiertos:
- `22/tcp` - SSH
- `80/tcp` - HTTP
- `443/tcp` - HTTPS
- `8000/tcp` - Backend API

---

## 🏥 Health Checks

### Post-Deployment

El workflow verifica automáticamente:

```bash
# Backend health
curl http://localhost:8000/health
# Esperado: 200 OK

# Frontend
curl http://localhost
# Esperado: 200 OK
```

### Health Endpoint

Agregar en `backend/api/app/main.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0",
        "timestamp": datetime.now().isoformat()
    }
```

---

## 📊 Monitoring & Logs

### Backend Logs

```bash
# Ver logs del servicio
sudo journalctl -u ontrackia-backend -f

# Últimos 100 logs
sudo journalctl -u ontrackia-backend -n 100
```

### Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

### Deployment Logs

En GitHub: **Actions → Deploy to Hetzner → Click on run**

---

## 🔄 Rollback

Si un deployment falla:

```bash
# SSH al servidor
ssh ontrackia@YOUR_SERVER_IP

# Navegar al repo
cd /opt/ontrackia/OJT

# Revertir al commit anterior
git log --oneline -5  # Ver commits
git reset --hard COMMIT_HASH

# Restart servicio
sudo systemctl restart ontrackia-backend
sudo systemctl reload nginx
```

---

## 🚨 Troubleshooting

### Deployment Falla

1. Verificar logs en GitHub Actions
2. SSH al servidor y revisar:
```bash
systemctl status ontrackia-backend
sudo journalctl -u ontrackia-backend -n 50
```

### Migraciones Fallan

```bash
# Verificar tabla de control
sudo -u postgres psql -d ontrackia_ojt -c "SELECT * FROM _migrations;"

# Re-aplicar manualmente
cd /opt/ontrackia/OJT/backend
source venv/bin/activate
python scripts/apply_migrations.py
```

### SSH No Funciona

```bash
# Verificar desde servidor local (console Hetzner)
sudo systemctl status sshd
sudo tail -f /var/log/auth.log

# Verificar llave en authorized_keys
cat /home/ontrackia/.ssh/authorized_keys
```

---

## 📈 Optimizaciones Futuras

### Blue-Green Deployment

```bash
# Mantener 2 versiones simultáneas
/opt/ontrackia/OJT-blue
/opt/ontrackia/OJT-green

# Switch de nginx entre versiones
```

### Docker Deployment

```bash
# Contenedorizar para aislamiento
docker-compose up -d
```

### CDN para Frontend

```bash
# Servir assets estáticos desde CDN
# Reducir carga del servidor
```

---

## 📚 Referencias

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SSH Hardening Guide](https://www.ssh.com/academy/ssh/hardening)
- [Nginx Best Practices](https://www.nginx.com/blog/nginx-best-practices/)
- [PostgreSQL Migration Strategies](https://www.postgresql.org/docs/current/sql-altertable.html)

---

## ✅ Checklist de Deployment

- [ ] Setup del servidor ejecutado
- [ ] Llave SSH agregada
- [ ] GitHub Secrets configurados
- [ ] Push a main ejecutado
- [ ] Health check pasado
- [ ] Frontend accesible
- [ ] Backend API respondiendo
- [ ] Migraciones aplicadas
- [ ] Knowledge items indexados
- [ ] Logs sin errores

---

**Fecha**: 2026-02-04  
**Versión**: 2.0 Ultimate  
**Equipo**: OnTrackia Dev Team
