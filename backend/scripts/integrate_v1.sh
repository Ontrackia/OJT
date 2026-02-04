#!/bin/bash
# OnTrackIA V1 - Final Integration Script
# Integrates PostgreSQL routers, applies migrations, and seeds database

set -e  # Exit on error

echo "🚀 OnTrackIA V1 - Final Integration"
echo "===================================="
echo ""

# Step 1: Install dependencies
echo "📦 Step 1/4: Installing dependencies..."
python -m pip install -q alembic psycopg2-binary sqlalchemy pydantic fastapi

# Step 2: Apply Alembic migrations
echo "🗄️  Step 2/4: Applying database migrations..."
cd "$(dirname "$0")/.."
export DATABASE_URL="postgresql://ontrackia_ojt:password@localhost:5432/ontrackia_ojt_db"

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "⚠️  PostgreSQL not running. Starting PostgreSQL..."
    echo "   Please ensure PostgreSQL is installed and configured."
    echo "   Database: ontrackia_ojt_db"
    echo "   User: ontrackia_ojt"
    echo "   Password: password"
    echo ""
    echo "   Run: createdb ontrackia_ojt_db"
    echo "        createuser ontrackia_ojt"
    exit 1
fi

# Apply migrations
python -m alembic upgrade head

# Step 3: Seed database
echo "🌱 Step 3/4: Seeding database with ICAO matrix..."
python scripts/seed_database.py

# Step 4: Verify integration
echo "✅ Step 4/4: Verifying integration..."
python -c "
from api.app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM risk_matrix'))
    count = result.scalar()
    print(f'   ✓ Risk Matrix entries: {count}')
    
    result = conn.execute(text('SELECT COUNT(*) FROM sms_reports'))
    count = result.scalar()
    print(f'   ✓ SMS Reports: {count}')
    
    result = conn.execute(text('SELECT COUNT(*) FROM audit_contexts'))
    count = result.scalar()
    print(f'   ✓ Audit Contexts: {count}')

print('')
print('✅ Integration complete!')
"

echo ""
echo "🎉 OnTrackIA V1 Core - Ready for Production"
echo "==========================================="
echo ""
echo "Next steps:"
echo "1. Start server: python rag_server_mistral.py"
echo "2. Test endpoints: curl http://localhost:8000/api/v2/sms/risk-matrix"
echo "3. Deploy to Hetzner: Follow DEPLOYMENT_CHECKLIST.md"
echo ""
