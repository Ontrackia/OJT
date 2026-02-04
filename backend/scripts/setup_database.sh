#!/bin/bash
# ==========================================
# OnTrackIA OJT V1 - Database Setup Script
# ==========================================

set -e  # Exit on error

echo "🚀 OnTrackIA OJT V1 - Database Setup"
echo "===================================="

# Check if PostgreSQL is running
echo ""
echo "📊 Checking PostgreSQL connection..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on localhost:5432"
    echo "   Please start PostgreSQL first"
    exit 1
fi
echo "✅ PostgreSQL is running"

# Check if database exists
echo ""
echo "🔍 Checking if database exists..."
DB_EXISTS=$(psql -h localhost -U ontrackia_ojt -lqt | cut -d \| -f 1 | grep -w ontrackia_ojt_db | wc -l)

if [ $DB_EXISTS -eq 0 ]; then
    echo "📦 Creating database ontrackia_ojt_db..."
    createdb -h localhost -U ontrackia_ojt ontrackia_ojt_db
    echo "✅ Database created"
else
    echo "✅ Database already exists"
fi

# Initialize tables
echo ""
echo "📋 Initializing database tables..."
cd "$(dirname "$0")/.."
python scripts/init_database.py

# Seed initial data
echo ""
echo "🌱 Seeding initial data..."
python scripts/seed_database.py

echo ""
echo "===================================="
echo "✅ DATABASE SETUP COMPLETE"
echo ""
echo "You can now start the server:"
echo "  uvicorn rag_server_mistral:app --reload --host 0.0.0.0 --port 8000"
