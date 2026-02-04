#!/bin/bash
# OnTrackIA V1-Core - Hetzner Server Deployment Script
# Run this script ON THE HETZNER SERVER

set -e

echo "🚀 OnTrackIA V1-Core - Hetzner Deployment"
echo "=========================================="

# Configuration
APP_DIR="/var/www/ontrackia"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
NGINX_CONF="/etc/nginx/sites-available/ontrackia"
DOMAIN="ontrackia.com"  # Change to your domain

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Phase 1: System Dependencies${NC}"
echo "========================================"

# Update system
apt-get update
apt-get upgrade -y

# Install required packages
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    fail2ban

echo -e "${GREEN}✅ System dependencies installed${NC}"

echo ""
echo -e "${YELLOW}Phase 2: PostgreSQL Setup${NC}"
echo "========================================"

# Start PostgreSQL
systemctl start postgresql
systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE ontrackia_v1;
CREATE USER ontrackia WITH ENCRYPTED PASSWORD 'CHANGE_THIS_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE ontrackia_v1 TO ontrackia;
ALTER DATABASE ontrackia_v1 OWNER TO ontrackia;
\q
EOF

echo -e "${GREEN}✅ PostgreSQL configured${NC}"

echo ""
echo -e "${YELLOW}Phase 3: Application Setup${NC}"
echo "========================================"

cd "$BACKEND_DIR"

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Apply migrations
alembic upgrade head

echo -e "${GREEN}✅ Backend configured${NC}"

echo ""
echo -e "${YELLOW}Phase 4: Systemd Services${NC}"
echo "========================================"

# Backend service
cat > /etc/systemd/system/ontrackia-backend.service << 'EOF'
[Unit]
Description=OnTrackIA V1-Core Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ontrackia/backend
Environment="PATH=/var/www/ontrackia/backend/venv/bin"
ExecStart=/var/www/ontrackia/backend/venv/bin/python rag_server_mistral.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload
systemctl enable ontrackia-backend
systemctl start ontrackia-backend

echo -e "${GREEN}✅ Backend service started${NC}"

echo ""
echo -e "${YELLOW}Phase 5: Nginx Configuration${NC}"
echo "========================================"

# Nginx config
cat > "$NGINX_CONF" << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    # Frontend
    root /var/www/ontrackia/frontend/build;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Frontend routes
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Service Worker
    location /service-worker.js {
        add_header Cache-Control "no-cache";
        try_files \$uri =404;
    }
}
EOF

# Enable site
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

echo -e "${GREEN}✅ Nginx configured${NC}"

echo ""
echo -e "${YELLOW}Phase 6: SSL Certificate${NC}"
echo "========================================"

# Get SSL certificate
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN

echo -e "${GREEN}✅ SSL certificate installed${NC}"

echo ""
echo -e "${YELLOW}Phase 7: Security Hardening${NC}"
echo "========================================"

# Configure fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo -e "${GREEN}✅ Security configured${NC}"

echo ""
echo -e "${YELLOW}Phase 8: Backup Configuration${NC}"
echo "========================================"

# Create backup script
cat > /usr/local/bin/backup-ontrackia.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ontrackia"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
sudo -u postgres pg_dump ontrackia_v1 | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Backup evidence vault
tar -czf "$BACKUP_DIR/evidence_$DATE.tar.gz" /var/www/ontrackia/backend/evidence_vault/

# Keep only last 30 days
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/backup-ontrackia.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-ontrackia.sh") | crontab -

echo -e "${GREEN}✅ Backup configured (daily at 2 AM)${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Your application is now running at:"
echo "  https://$DOMAIN"
echo ""
echo "Services status:"
systemctl status ontrackia-backend --no-pager
systemctl status nginx --no-pager
echo ""
echo "Next steps:"
echo "1. Test the application"
echo "2. Configure monitoring"
echo "3. Review logs: journalctl -u ontrackia-backend -f"
