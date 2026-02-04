# OnTrackIA OJT V1 - Deployment Guide

## 🎯 Objetivo

Desplegar OnTrackIA OJT V1 en Hetzner con PostgreSQL, Mistral LLM, y SSL.

---

## 📋 Pre-requisitos

### En Hetzner Server

- Ubuntu 22.04 LTS
- PostgreSQL 15
- Python 3.10+
- Nginx
- Certbot (Let's Encrypt)

---

## 🚀 Paso 1: Configurar PostgreSQL

```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER ontrackia_ojt WITH PASSWORD 'CHANGE_THIS_PASSWORD';
CREATE DATABASE ontrackia_ojt_db OWNER ontrackia_ojt;
GRANT ALL PRIVILEGES ON DATABASE ontrackia_ojt_db TO ontrackia_ojt;
\q
EOF
```

---

## 🚀 Paso 2: Clonar y Configurar Backend

```bash
# Clonar repositorio
cd /var/www
git clone <YOUR_REPO_URL> ontrackia_ojt
cd ontrackia_ojt/backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env
```

### Configurar `.env`

```bash
DATABASE_URL=postgresql://ontrackia_ojt:YOUR_PASSWORD@localhost:5432/ontrackia_ojt_db
MISTRAL_API_KEY=c3ko2dPmh4XTPSEZAz058KsS8W22RXMH
CHROMADB_PATH=/var/www/ontrackia_ojt/backend/data/chromadb
JWT_SECRET_KEY=GENERATE_RANDOM_SECRET_HERE
ENVIRONMENT=production
```

---

## 🚀 Paso 3: Inicializar Base de Datos

```bash
# Ejecutar script de setup
cd /var/www/ontrackia_ojt/backend
source venv/bin/activate
python scripts/init_database.py
python scripts/seed_database.py
```

---

## 🚀 Paso 4: Configurar Systemd Service

```bash
sudo nano /etc/systemd/system/ontrackia.service
```

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
# Habilitar y arrancar servicio
sudo systemctl daemon-reload
sudo systemctl enable ontrackia
sudo systemctl start ontrackia
sudo systemctl status ontrackia
```

---

## 🚀 Paso 5: Configurar Nginx con SSL

```bash
sudo apt install -y nginx certbot python3-certbot-nginx

# Configurar Nginx
sudo nano /etc/nginx/sites-available/ontrackia
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
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
}
```

```bash
# Activar sitio
sudo ln -s /etc/nginx/sites-available/ontrackia /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtener certificado SSL
sudo certbot --nginx -d your-domain.com
```

---

## 🚀 Paso 6: Desplegar Frontend

```bash
cd /var/www/ontrackia_ojt/frontend

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Build frontend
npm install
npm run build

# Configurar Nginx para servir frontend
sudo nano /etc/nginx/sites-available/ontrackia
```

Agregar al bloque `server`:

```nginx
    location / {
        root /var/www/ontrackia_ojt/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        # ... (resto de configuración proxy)
    }
```

```bash
sudo systemctl reload nginx
```

---

## ✅ Verificación

1. **Backend Health Check:**

   ```bash
   curl https://your-domain.com/api/v2/audit/stats
   ```

2. **Mistral Integration:**

   ```bash
   curl https://your-domain.com/
   # Debe mostrar: "mistral_enabled": true
   ```

3. **PostgreSQL Connection:**

   ```bash
   sudo -u postgres psql -d ontrackia_ojt_db -c "SELECT COUNT(*) FROM risk_matrix;"
   # Debe retornar 10 (5 severity + 5 probability)
   ```

4. **SSL Certificate:**

   ```bash
   curl -I https://your-domain.com
   # Debe retornar 200 con headers de seguridad
   ```

---

## 🔧 Troubleshooting

### Backend no arranca

```bash
sudo journalctl -u ontrackia -f
```

### PostgreSQL connection error

```bash
sudo -u postgres psql
\l  # Listar bases de datos
\du  # Listar usuarios
```

### Nginx errors

```bash
sudo tail -f /var/log/nginx/error.log
```

---

## 📊 Monitoreo

```bash
# Ver logs del backend
sudo journalctl -u ontrackia -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log

# Verificar uso de recursos
htop
```

---

## 🔐 Seguridad Post-Deployment

1. **Cambiar contraseñas por defecto**
2. **Configurar firewall (ufw)**
3. **Habilitar fail2ban**
4. **Configurar backups automáticos de PostgreSQL**

---

## 📞 Soporte

Para Travis: El sistema estará disponible en `https://your-domain.com`

Credenciales iniciales se enviarán por canal seguro.
