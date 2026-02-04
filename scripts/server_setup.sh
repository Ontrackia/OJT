#!/bin/bash
#
# OnTrackIA OJT V2.0 - Server Setup Script
# =========================================
# Configuración inicial del servidor Hetzner con Protocolo Búnker
#
# Autor: OnTrackia Dev Team
# Fecha: 2026-02-04

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}OnTrackIA OJT V2.0 - Server Setup${NC}"
echo -e "${BLUE}Protocolo Búnker - SSH Hardening${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 1. Actualizar sistema
echo -e "${YELLOW}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    ufw \
    fail2ban

# 3. Crear usuario ontrackia
echo -e "\n${YELLOW}👤 Creating ontrackia user...${NC}"
if ! id -u ontrackia > /dev/null 2>&1; then
    sudo useradd -m -s /bin/bash ontrackia
    echo -e "${GREEN}✓ User created${NC}"
else
    echo -e "${GREEN}✓ User already exists${NC}"
fi

# 4. Configurar SSH - PROTOCOLO BÚNKER
echo -e "\n${YELLOW}🔐 Configuring SSH (Búnker Protocol)...${NC}"

# Backup de configuración original
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Configuración SSH segura
sudo tee /etc/ssh/sshd_config > /dev/null <<EOF
# OnTrackIA OJT V2.0 - SSH Búnker Configuration
# ==============================================

# PROTOCOLO BÚNKER: Solo autenticación por llave SSH
PasswordAuthentication no
PubkeyAuthentication yes
ChallengeResponseAuthentication no

# Deshabilitar root login
PermitRootLogin no

# Solo usuario ontrackia
AllowUsers ontrackia

# Puerto SSH (cambiar si es necesario)
Port 22

# Protocolo SSH 2 solamente
Protocol 2

# Key exchange algorithms (solo seguros)
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org

# Ciphers seguros
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com

# MACs seguros
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Timeouts
ClientAliveInterval 300
ClientAliveCountMax 2

# Logging
SyslogFacility AUTH
LogLevel VERBOSE

# Banners
Banner /etc/ssh/banner

# Subsistemas
Subsystem sftp /usr/lib/openssh/sftp-server
EOF

# Crear banner
sudo tee /etc/ssh/banner > /dev/null <<EOF
******************************************************
*                                                    *
*            OnTrackIA OJT V2.0 - Búnker            *
*                                                    *
*    Acceso Autorizado Solamente                    *
*    Todas las acciones son registradas             *
*                                                    *
******************************************************
EOF

echo -e "${GREEN}✓ SSH configured${NC}"

# 5. Configurar directorio .ssh para ontrackia
echo -e "\n${YELLOW}🔑 Setting up SSH keys...${NC}"
sudo -u ontrackia mkdir -p /home/ontrackia/.ssh
sudo -u ontrackia chmod 700 /home/ontrackia/.ssh

# Crear archivo authorized_keys
sudo -u ontrackia touch /home/ontrackia/.ssh/authorized_keys
sudo -u ontrackia chmod 600 /home/ontrackia/.ssh/authorized_keys

echo -e "${YELLOW}⚠️  IMPORTANTE: Agregar tu llave pública SSH a:${NC}"
echo -e "${YELLOW}   /home/ontrackia/.ssh/authorized_keys${NC}"
echo -e "${YELLOW}   Antes de reiniciar SSH!${NC}\n"

read -p "¿Ya agregaste tu llave SSH? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Abortando. Agrega tu llave SSH primero.${NC}"
    exit 1
fi

# 6. Configurar Firewall
echo -e "\n${YELLOW}🔥 Configuring firewall (UFW)...${NC}"
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 8000/tcp # Backend API
sudo ufw --force enable

echo -e "${GREEN}✓ Firewall configured${NC}"

# 7. Configurar Fail2Ban
echo -e "\n${YELLOW}🛡️  Configuring Fail2Ban...${NC}"
sudo tee /etc/fail2ban/jail.local > /dev/null <<EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
EOF

sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

echo -e "${GREEN}✓ Fail2Ban configured${NC}"

# 8. Clonar repositorio
echo -e "\n${YELLOW}📥 Cloning repository...${NC}"
sudo mkdir -p /opt/ontrackia
sudo chown ontrackia:ontrackia /opt/ontrackia

sudo -u ontrackia git clone https://github.com/Ontrackia/OJT.git /opt/ontrackia/OJT || {
    echo -e "${YELLOW}⚠️  Repository already exists, pulling latest...${NC}"
    cd /opt/ontrackia/OJT
    sudo -u ontrackia git pull origin main
}

echo -e "${GREEN}✓ Repository ready${NC}"

# 9. Configurar Python environment
echo -e "\n${YELLOW}🐍 Setting up Python environment...${NC}"
cd /opt/ontrackia/OJT/backend

sudo -u ontrackia python3.11 -m venv venv
sudo -u ontrackia venv/bin/pip install --upgrade pip
sudo -u ontrackia venv/bin/pip install -r requirements.txt

echo -e "${GREEN}✓ Python environment ready${NC}"

# 10. Configurar PostgreSQL
echo -e "\n${YELLOW}🗄️  Configuring PostgreSQL...${NC}"

sudo -u postgres psql <<EOF
CREATE USER ontrackia WITH PASSWORD 'CHANGE_ME_IN_PRODUCTION';
CREATE DATABASE ontrackia_ojt OWNER ontrackia;
GRANT ALL PRIVILEGES ON DATABASE ontrackia_ojt TO ontrackia;
EOF

echo -e "${GREEN}✓ PostgreSQL configured${NC}"
echo -e "${YELLOW}⚠️  IMPORTANTE: Cambiar contraseña en producción!${NC}"

# 11. Crear archivo .env
echo -e "\n${YELLOW}⚙️  Creating .env file...${NC}"

sudo -u ontrackia tee /opt/ontrackia/OJT/backend/.env > /dev/null <<EOF
# OnTrackIA OJT V2.0 - Production Environment
# ============================================

# Database
POSTGRES_HOST=localhost
POSTGRES_DB=ontrackia_ojt
POSTGRES_USER=ontrackia
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION

# JWT
JWT_SECRET_KEY=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256

# API
API_HOST=0.0.0.0
API_PORT=8000

# Redis
REDIS_URL=redis://localhost:6379

# Environment
ENVIRONMENT=production
DEBUG=false
EOF

echo -e "${GREEN}✓ .env file created${NC}"

# 12. Crear servicio systemd para backend
echo -e "\n${YELLOW}⚙️  Creating systemd service...${NC}"

sudo tee /etc/systemd/system/ontrackia-backend.service > /dev/null <<EOF
[Unit]
Description=OnTrackIA OJT V2.0 Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=ontrackia
WorkingDirectory=/opt/ontrackia/OJT/backend
Environment="PATH=/opt/ontrackia/OJT/backend/venv/bin"
ExecStart=/opt/ontrackia/OJT/backend/venv/bin/uvicorn api.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ontrackia-backend

echo -e "${GREEN}✓ Backend service created${NC}"

# 13. Configurar Nginx
echo -e "\n${YELLOW}🌐 Configuring Nginx...${NC}"

sudo tee /etc/nginx/sites-available/ontrackia > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        root /var/www/ontrackia/dist;
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/ontrackia /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

sudo mkdir -p /var/www/ontrackia
sudo chown -R ontrackia:ontrackia /var/www/ontrackia

sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx

echo -e "${GREEN}✓ Nginx configured${NC}"

# 14. Reiniciar SSH (CRÍTICO)
echo -e "\n${YELLOW}🔄 Restarting SSH service...${NC}"
echo -e "${RED}⚠️  ADVERTENCIA: Asegúrate de tener tu llave SSH configurada!${NC}"

read -p "¿Continuar con reinicio de SSH? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo systemctl restart sshd
    echo -e "${GREEN}✓ SSH restarted${NC}"
else
    echo -e "${YELLOW}⏭️  Skipped SSH restart${NC}"
    echo -e "${YELLOW}   Ejecuta manualmente: sudo systemctl restart sshd${NC}"
fi

# Final
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Server setup completed!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}NEXT STEPS:${NC}"
echo -e "1. Cambiar contraseña de PostgreSQL"
echo -e "2. Configurar GitHub Secrets:"
echo -e "   - HETZNER_HOST"
echo -e "   - HETZNER_USER (ontrackia)"
echo -e "   - HETZNER_SSH_KEY (llave privada)"
echo -e "3. Push a main para deployment automático"
echo -e "4. Verificar servicio: systemctl status ontrackia-backend\n"

echo -e "${GREEN}🎉 OnTrackIA OJT V2.0 ready for deployment!${NC}\n"
