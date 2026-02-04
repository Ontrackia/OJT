# 🚀 OnTrackIA OJT V1 - Checklist de Despliegue

## ✅ Pre-Despliegue (Completado)

- [x] Modelos PostgreSQL creados (SMS, Audit, Security)
- [x] Alembic configurado
- [x] Row-Level Security (RLS) implementado
- [x] Scripts de inicialización (`init_database.py`, `seed_database.py`)
- [x] PDF Generator con SHA-256 forense
- [x] Guía de despliegue (`DEPLOYMENT.md`)
- [x] Configuración Nginx + Systemd

---

## 📋 Checklist de Despliegue en Hetzner

### 1. Preparación del Servidor

```bash
# SSH al servidor
ssh root@<HETZNER_IP>

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y postgresql postgresql-contrib python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git
```

- [ ] Servidor actualizado
- [ ] PostgreSQL instalado
- [ ] Nginx instalado
- [ ] Certbot instalado

---

### 2. Configurar PostgreSQL

```bash
# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER ontrackia_ojt WITH PASSWORD 'SECURE_PASSWORD_HERE';
CREATE DATABASE ontrackia_ojt_db OWNER ontrackia_ojt;
GRANT ALL PRIVILEGES ON DATABASE ontrackia_ojt_db TO ontrackia_ojt;
\q
EOF

# Verificar conexión
psql -h localhost -U ontrackia_ojt -d ontrackia_ojt_db -c "SELECT version();"
```

- [ ] Usuario PostgreSQL creado
- [ ] Base de datos creada
- [ ] Conexión verificada

---

### 3. Clonar y Configurar Backend

```bash
# Clonar repositorio
cd /var/www
git clone <YOUR_REPO_URL> ontrackia_ojt
cd ontrackia_ojt/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

- [ ] Repositorio clonado
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas

---

### 4. Configurar Variables de Entorno

```bash
# Editar .env
nano /var/www/ontrackia_ojt/backend/.env
```

**Contenido del `.env`:**

```bash
DATABASE_URL=postgresql://ontrackia_ojt:SECURE_PASSWORD_HERE@localhost:5432/ontrackia_ojt_db
MISTRAL_API_KEY=c3ko2dPmh4XTPSEZAz058KsS8W22RXMH
CHROMADB_PATH=/var/www/ontrackia_ojt/backend/data/chromadb
JWT_SECRET_KEY=<GENERATE_RANDOM_64_CHARS>
ENCRYPTION_KEY=<GENERATE_RANDOM_64_CHARS>
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-domain.com
```

- [ ] `.env` configurado
- [ ] `DATABASE_URL` actualizado
- [ ] `JWT_SECRET_KEY` generado
- [ ] `ENCRYPTION_KEY` generado

---

### 5. Inicializar Base de Datos

```bash
cd /var/www/ontrackia_ojt/backend
source venv/bin/activate

# Ejecutar scripts
python scripts/init_database.py
python scripts/seed_database.py
```

**Verificar:**

```bash
psql -h localhost -U ontrackia_ojt -d ontrackia_ojt_db -c "SELECT COUNT(*) FROM risk_matrix;"
# Debe retornar: 10
```

- [ ] Tablas creadas
- [ ] RLS aplicado
- [ ] Risk Matrix seeded (10 registros)

---

### 6. Configurar Systemd Service

```bash
sudo nano /etc/systemd/system/ontrackia.service
```

**Contenido:**

```ini
[Unit]
Description=OnTrackIA OJT Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ontrackia_ojt/backend
Environment="PATH=/var/www/ontrackia_ojt/backend/venv/bin"
ExecStart=/var/www/ontrackia_ojt/backend/venv/bin/uvicorn rag_server_mistral:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y arrancar
sudo systemctl daemon-reload
sudo systemctl enable ontrackia
sudo systemctl start ontrackia
sudo systemctl status ontrackia
```

- [ ] Service creado
- [ ] Service habilitado
- [ ] Service corriendo (status: active)

---

### 7. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/ontrackia
```

**Contenido:**

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /var/www/ontrackia_ojt/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/ontrackia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

- [ ] Nginx configurado
- [ ] Configuración válida (`nginx -t`)
- [ ] Nginx recargado

---

### 8. Configurar SSL con Let's Encrypt

```bash
sudo certbot --nginx -d your-domain.com
```

**Seguir prompts:**

- Email para notificaciones
- Aceptar términos
- Redirigir HTTP a HTTPS (opción 2)

- [ ] Certificado SSL obtenido
- [ ] Redirección HTTPS configurada

---

### 9. Desplegar Frontend

```bash
cd /var/www/ontrackia_ojt/frontend

# Instalar Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Build frontend
npm install
npm run build

# Verificar dist/
ls -la dist/
```

- [ ] Node.js instalado
- [ ] Dependencias instaladas
- [ ] Build completado (`dist/` existe)

---

## ✅ Verificación Post-Despliegue

### 1. Backend Health Check

```bash
curl https://your-domain.com/api/v2/audit/stats
```

**Esperado:** JSON con estadísticas

- [ ] Backend responde

### 2. Mistral Integration

```bash
curl https://your-domain.com/
```

**Esperado:** `"mistral_enabled": true`

- [ ] Mistral habilitado

### 3. PostgreSQL Connection

```bash
sudo -u postgres psql -d ontrackia_ojt_db -c "SELECT COUNT(*) FROM risk_matrix;"
```

**Esperado:** `10`

- [ ] PostgreSQL conectado

### 4. PDF Generation

```bash
curl -o test.pdf https://your-domain.com/api/v2/pdf/audit/TEST-001
file test.pdf
```

**Esperado:** `PDF document`

- [ ] PDF se genera correctamente

### 5. SSL Certificate

```bash
curl -I https://your-domain.com
```

**Esperado:** `HTTP/2 200` con headers de seguridad

- [ ] SSL funcionando

---

## 🔐 Seguridad Post-Despliegue

```bash
# Configurar firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Instalar fail2ban
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

- [ ] Firewall configurado
- [ ] Fail2ban instalado

---

## 📊 Monitoreo

```bash
# Ver logs del backend
sudo journalctl -u ontrackia -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Ver logs de PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

---

## 🎯 Entrega a Travis

**URL de producción:** `https://your-domain.com`

**Funcionalidades disponibles:**

- ✅ Auditorías EASA Part-145
- ✅ SMS Safety Reports con ICAO 5x5
- ✅ Root Cause Analysis (RCA)
- ✅ PDF con sello SHA-256 forense
- ✅ Mistral LLM (Senior Auditor Coach)
- ✅ Persistencia PostgreSQL
- ✅ Row-Level Security

**Credenciales:** (enviar por canal seguro)

---

## 🆘 Troubleshooting

### Backend no arranca

```bash
sudo journalctl -u ontrackia -n 50
```

### PostgreSQL connection error

```bash
sudo -u postgres psql
\l
\du
```

### Nginx 502 Bad Gateway

```bash
sudo systemctl status ontrackia
curl http://localhost:8000/api/v2/audit/stats
```

### SSL no funciona

```bash
sudo certbot renew --dry-run
```

---

**¡OnTrackIA OJT V1 listo para producción! 🚀**
