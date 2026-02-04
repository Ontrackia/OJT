#!/bin/bash
# OnTrackIA V1-Core - Production Deployment Script
# Automated deployment to Hetzner with security checks

set -e  # Exit on error

echo "🚀 OnTrackIA V1-Core - Production Deployment"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Users/gregorioromerovega/Desktop/OnTrackIA_OJT"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo -e "${YELLOW}Phase 1: Frontend Build${NC}"
echo "========================================"

cd "$FRONTEND_DIR"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install Node.js first.${NC}"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Security audit
echo "🔒 Running security audit..."
npm audit --production || echo -e "${YELLOW}⚠️  Security warnings found. Review before deployment.${NC}"

# Build production
echo "🏗️  Building production bundle..."
npm run build

if [ -d "build" ]; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
    echo "   Build size: $(du -sh build | cut -f1)"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Phase 2: Backend Preparation${NC}"
echo "========================================"

cd "$BACKEND_DIR"

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt --quiet

# Check database migrations
echo "🗄️  Checking database migrations..."
alembic current

echo ""
echo -e "${YELLOW}Phase 3: Pre-deployment Checks${NC}"
echo "========================================"

# Check environment variables
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env file with:"
    echo "  - DATABASE_URL"
    echo "  - MISTRAL_API_KEY"
    echo "  - JWT_SECRET_KEY"
    echo "  - ENCRYPTION_KEY"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Check PostgreSQL connection
echo "🔌 Testing PostgreSQL connection..."
python -c "
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))
try:
    conn = engine.connect()
    print('✅ PostgreSQL connection successful')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    exit(1)
" || exit 1

echo ""
echo -e "${GREEN}✅ All pre-deployment checks passed${NC}"
echo ""
echo -e "${YELLOW}Phase 4: Deployment Instructions${NC}"
echo "========================================"
echo ""
echo "To deploy to Hetzner, run these commands on the server:"
echo ""
echo "1. SSH to server:"
echo "   ssh root@<hetzner-ip>"
echo ""
echo "2. Clone/pull repository:"
echo "   cd /var/www"
echo "   git clone <repo-url> ontrackia"
echo "   cd ontrackia"
echo ""
echo "3. Copy environment variables:"
echo "   cp .env.example .env"
echo "   nano .env  # Configure production values"
echo ""
echo "4. Run deployment script on server:"
echo "   chmod +x deploy_hetzner.sh"
echo "   ./deploy_hetzner.sh"
echo ""
echo "5. Configure Nginx + SSL:"
echo "   Follow DEPLOYMENT_GUIDE.md section 'Nginx Configuration'"
echo ""
echo -e "${GREEN}✅ Local build ready for deployment${NC}"
echo ""
echo "Next steps:"
echo "1. Transfer build/ directory to Hetzner"
echo "2. Apply database migrations on server"
echo "3. Configure systemd services"
echo "4. Setup SSL with Certbot"
echo "5. Start services and verify"
