#!/bin/bash
#
# OnTrackIA OJT V2.0 - Deployment Script
# =======================================
# Deploy Cielos Abiertos to Hetzner CPX42
#
# Usage: ./deploy_cielos_abiertos.sh
#

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SERVER="95.217.17.102"
USER="root"
PROJECT_DIR="/root/ontrackia_ojt"

echo "======================================================================"
echo "  ONTRACKIA OJT V2.0 - DEPLOYMENT: CIELOS ABIERTOS"
echo "======================================================================"
echo ""
echo -e "${BLUE}🌍 Deploying Global Regulatory System${NC}"
echo -e "   Server: ${SERVER}"
echo -e "   Project: ${PROJECT_DIR}"
echo ""

# 1. Pull latest code
echo -e "${BLUE}📥 Step 1: Pulling latest code from GitHub...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt
git pull origin main
echo "✅ Code updated"
ENDSSH

# 2. Install dependencies
echo ""
echo -e "${BLUE}📦 Step 2: Installing Python dependencies...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt/backend
pip install pdfplumber lxml tqdm beautifulsoup4 chromadb sentence-transformers PyPDF2
python3 -c "import pdfplumber, lxml, tqdm, chromadb, sentence_transformers; print('✅ All dependencies installed')"
ENDSSH

# 3. Create knowledge base directory
echo ""
echo -e "${BLUE}📁 Step 3: Creating knowledge base structure...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
mkdir -p /root/ontrackia_ojt/backend/knowledge_base/global
mkdir -p /root/ontrackia_ojt/backend/data/chromadb
chmod +x /root/ontrackia_ojt/backend/scripts/*.sh
echo "✅ Directory structure created"
ENDSSH

# 4. Download regulatory documents (sample - ANAC Brasil)
echo ""
echo -e "${BLUE}🇧🇷 Step 4: Testing regulatory crawler (ANAC Brasil)...${NC}"
echo -e "${YELLOW}   This is a test run - full crawl will be done separately${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt/backend
# Test with one country first
python3 scripts/regulatory_crawler.py --territory BRAZIL --output ./knowledge_base/global || echo "⚠️  Crawler test skipped (will run manually)"
ENDSSH

# 5. Index knowledge base
echo ""
echo -e "${BLUE}🧠 Step 5: Indexing knowledge base into ChromaDB...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt/backend

# Check if we have documents to index
KNOWLEDGE_DIR="./knowledge_base/global"
if [ -d "$KNOWLEDGE_DIR" ] && [ "$(find $KNOWLEDGE_DIR -type f | wc -l)" -gt 0 ]; then
    echo "Found documents to index"
    python3 scripts/rag_indexer.py \
        --source "$KNOWLEDGE_DIR" \
        --chromadb-path ./data/chromadb \
        --test-query "ANAC RBAC 145 maintenance organization"
else
    echo "⚠️  No documents found yet - run crawler first"
fi
ENDSSH

# 6. Restart services
echo ""
echo -e "${BLUE}🔄 Step 6: Restarting backend service...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt/backend
# Kill existing server if running
pkill -f "python.*server.py" || true
sleep 2

# Start in background with nohup
nohup python3 server.py > server.log 2>&1 &
echo $! > server.pid

sleep 3

# Check if running
if ps -p $(cat server.pid) > /dev/null 2>&1; then
    echo "✅ Backend server running (PID: $(cat server.pid))"
else
    echo "⚠️  Backend server failed to start - check server.log"
fi
ENDSSH

# 7. Check ChromaDB status
echo ""
echo -e "${BLUE}📊 Step 7: Verifying ChromaDB status...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt/backend
python3 - << 'ENDPYTHON'
import chromadb
from chromadb.config import Settings

try:
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory="./data/chromadb"
    ))
    
    collection = client.get_collection("ontrackia_knowledge")
    count = collection.count()
    
    print(f"✅ ChromaDB operational")
    print(f"   Documents indexed: {count}")
    
    if count > 0:
        print("   🎯 RAG system ready for territorial queries")
except Exception as e:
    print(f"⚠️  ChromaDB not initialized yet: {e}")
    print("   Run indexer manually: python3 scripts/rag_indexer.py --source ./knowledge_base/global")
ENDPYTHON
ENDSSH

# 8. Test territorial query
echo ""
echo -e "${BLUE}🧪 Step 8: Testing territorial RAG query...${NC}"
ssh ${USER}@${SERVER} << 'ENDSSH'
cd /root/ontrackia_ojt/backend
curl -X POST http://localhost:8000/api/v2/audit/analyze \
    -H "Content-Type: application/json" \
    -d '{
        "evidence_id": "test",
        "task_description": "OJT record signature requirements",
        "territory": "BRAZIL",
        "context": {}
    }' 2>/dev/null | python3 -m json.tool || echo "⚠️  Test query skipped (no evidence yet)"
ENDSSH

echo ""
echo "======================================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETED${NC}"
echo "======================================================================"
echo ""
echo "📊 Next Steps:"
echo ""
echo "1. Full Regulatory Crawl (run on server):"
echo "   cd /root/ontrackia_ojt/backend"
echo "   python3 scripts/regulatory_crawler.py --all"
echo ""
echo "2. Monitor ChromaDB indexing:"
echo "   tail -f /root/ontrackia_ojt/backend/server.log"
echo ""
echo "3. Test territorial queries in Dashboard:"
echo "   http://95.217.17.102:3000"
echo "   Login → Dashboard Auditor → Select Territory → Analyze"
echo ""
echo "🌍 Cielos Abiertos System Activated!"
echo ""
