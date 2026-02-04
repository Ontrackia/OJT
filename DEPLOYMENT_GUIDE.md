# 🚀 OnTrackIA V1-Core - Deployment Guide

**Objetivo:** Despliegue en Hetzner con SSL y PostgreSQL  
**Tiempo estimado:** 60 minutos  
**Fecha:** 2026-02-04

---

## 📋 PRE-REQUISITOS

### **Servidor Hetzner:**

- Ubuntu 22.04 LTS
- 4GB RAM mínimo
- 50GB SSD
- IP pública asignada
- Dominio configurado (ej: ontrackia.com)

### **Credenciales necesarias:**

- SSH key para acceso root
- Mistral API Key
- Encryption keys (generar nuevas para producción)

---

## 🔧 PASO 1: Configuración Inicial del Servidor

```bash
# SSH al servidor
ssh root@your-server-ip

# Actualizar sistema
apt update && apt upgrade -y

# Instalar dependencias base
apt install -y git nginx certbot python3-certbot-nginx \
    postgresql postgresql-contrib python3-pip python3-venv \
    build-essential libpq-dev

# Crear usuario ontrackia
adduser ontrackia
usermod -aG sudo ontrackia

# Configurar firewall
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw enable
```

---

## 🗄️ PASO 2: Configurar PostgreSQL

```bash
# Cambiar a usuario postgres
sudo -u postgres psql

# Crear database y usuario
CREATE DATABASE ontrackia_ojt_db;
CREATE USER ontrackia_ojt WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE ontrackia_ojt_db TO ontrackia_ojt;

# Habilitar extensiones
\c ontrackia_ojt_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

\q

# Configurar acceso remoto (opcional)
sudo nano /etc/postgresql/14/main/postgresql.conf
# Descomentar: listen_addresses = 'localhost'

sudo systemctl restart postgresql
```

---

## 📦 PASO 3: Clonar Repositorio

```bash
# Cambiar a usuario ontrackia
su - ontrackia

# Clonar repositorio
git clone git@github.com:Ontrackia/V1-Core.git
cd V1-Core

# Verificar estructura
ls -la
# Debe mostrar: backend/, frontend/, README.md, etc.
```

---

## 🐍 PASO 4: Configurar Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios de almacenamiento
sudo mkdir -p /var/ontrackia/evidence_vault
sudo mkdir -p /var/ontrackia/knowledge_vault
sudo chown -R ontrackia:ontrackia /var/ontrackia

# Configurar variables de entorno
cp .env.example .env
nano .env
```

### **Configuración .env (CRÍTICO):**

```bash
# Database
DATABASE_URL=postgresql://ontrackia_ojt:CHANGE_THIS_PASSWORD@localhost:5432/ontrackia_ojt_db

# Mistral AI
MISTRAL_API_KEY=your_mistral_api_key_here

# Security (GENERAR NUEVAS CLAVES)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EVIDENCE_ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Environment
ENVIRONMENT=production
ALLOWED_ORIGINS=https://ontrackia.com,https://www.ontrackia.com

# Paths
AI_LOGS_DIR=/var/ontrackia/ai_logs
EVIDENCE_VAULT_PATH=/var/ontrackia/evidence_vault
KNOWLEDGE_VAULT_PATH=/var/ontrackia/knowledge_vault
```

---

## 🗃️ PASO 5: Aplicar Migraciones

```bash
# Aplicar migraciones Alembic
alembic upgrade head

# Verificar tablas creadas
psql -U ontrackia_ojt -d ontrackia_ojt_db -c "\dt"

# Verificar RLS activo
psql -U ontrackia_ojt -d ontrackia_ojt_db -c "
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND rowsecurity = true;
"

# Seed database (ICAO Matrix + Admin)
python scripts/seed_database.py
```

---

## 🌐 PASO 6: Configurar Frontend

```bash
cd ../frontend

# Instalar Node.js 18 (si no está)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env.production
nano .env.production
```

### **Configuración .env.production:**

```bash
VITE_API_URL=https://ontrackia.com/api
VITE_ENVIRONMENT=production
```

```bash
# Build para producción
npm run build

# Verificar build
ls -la dist/
```

---

## 🔧 PASO 7: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/ontrackia
```

### **Configuración Nginx:**

```nginx
# Backend API
server {
    listen 80;
    server_name api.ontrackia.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend
server {
    listen 80;
    server_name ontrackia.com www.ontrackia.com;

    root /home/ontrackia/V1-Core/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Activar configuración
sudo ln -s /etc/nginx/sites-available/ontrackia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🔒 PASO 8: Configurar SSL (Certbot)

```bash
# Obtener certificados SSL
sudo certbot --nginx -d ontrackia.com -d www.ontrackia.com -d api.ontrackia.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

---

## 🔄 PASO 9: Configurar Systemd Services

### **Backend Service:**

```bash
sudo nano /etc/systemd/system/ontrackia-backend.service
```

```ini
[Unit]
Description=OnTrackIA V1-Core Backend
After=network.target postgresql.service

[Service]
Type=simple
User=ontrackia
WorkingDirectory=/home/ontrackia/V1-Core/backend
Environment="PATH=/home/ontrackia/V1-Core/backend/venv/bin"
ExecStart=/home/ontrackia/V1-Core/backend/venv/bin/python rag_server_mistral.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activar servicio
sudo systemctl daemon-reload
sudo systemctl enable ontrackia-backend
sudo systemctl start ontrackia-backend

# Verificar estado
sudo systemctl status ontrackia-backend
```

---

## ✅ PASO 10: Verificación Final

```bash
# 1. Verificar backend
curl http://localhost:8000/health
# Esperado: {"status": "healthy"}

# 2. Verificar PostgreSQL
psql -U ontrackia_ojt -d ontrackia_ojt_db -c "SELECT COUNT(*) FROM risk_matrix;"
# Esperado: 25 (ICAO 5x5)

# 3. Verificar SSL
curl https://ontrackia.com
# Esperado: HTML del frontend

# 4. Verificar API
curl https://ontrackia.com/api/v2/sms/risk-matrix
# Esperado: JSON con matriz ICAO

# 5. Verificar Master Audit Log
curl -X POST https://ontrackia.com/api/v2/audit-trail/verify-integrity
# Esperado: {"status": "VERIFIED"}
```

---

## 📊 PASO 11: Monitoreo

```bash
# Ver logs backend
sudo journalctl -u ontrackia-backend -f

# Ver logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Ver logs PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

---

## 🔐 PASO 12: Seguridad Post-Despliegue

```bash
# 1. Deshabilitar login root SSH
sudo nano /etc/ssh/sshd_config
# PermitRootLogin no
sudo systemctl restart sshd

# 2. Configurar fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 3. Configurar backups automáticos PostgreSQL
sudo nano /etc/cron.daily/postgres-backup
```

```bash
#!/bin/bash
pg_dump -U ontrackia_ojt ontrackia_ojt_db | gzip > /var/backups/ontrackia_$(date +%Y%m%d).sql.gz
find /var/backups -name "ontrackia_*.sql.gz" -mtime +7 -delete
```

```bash
sudo chmod +x /etc/cron.daily/postgres-backup
```

---

## 🎉 DESPLIEGUE COMPLETADO

### **URLs de acceso:**

- Frontend: <https://ontrackia.com>
- API: <https://ontrackia.com/api>
- Docs: <https://ontrackia.com/api/docs>

### **Credenciales iniciales:**

- Admin email: <admin@ontrackia.com>
- Password: (generado en seed_database.py)

### **Próximos pasos:**

1. Cambiar password de admin
2. Crear usuarios para Travis y Victoria
3. Subir MOE en Knowledge Management
4. Realizar audit de prueba
5. Generar primer PDF forense

---

**OnTrackIA V1-Core está ONLINE** 🚀
