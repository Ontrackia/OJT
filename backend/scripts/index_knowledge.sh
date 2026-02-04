#!/bin/bash
#
# OnTrackIA OJT V2.0 - RAG Indexation Launcher
# ==============================================
# Script para iniciar la indexación masiva de conocimientos
#
# Autor: OnTrackia Dev Team
# Fecha: 2026-02-04

set -e

echo "======================================================================"
echo "  ONTRACKIA OJT V2.0 - CEREBRO TRIDENTE ACTIVATION"
echo "======================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$BACKEND_DIR")"

CHROMADB_PATH="${BACKEND_DIR}/data/chromadb"
INDEXER_SCRIPT="${BACKEND_DIR}/scripts/rag_indexer.py"

# Default knowledge sources
KNOWLEDGE_SOURCES=(
    "$HOME/Desktop/ONTRACKIA_RECUPERADO"
    "${PROJECT_ROOT}/knowledge"
    "${PROJECT_ROOT}/docs"
)

echo -e "${BLUE}🔍 Configuración:${NC}"
echo "   Backend: $BACKEND_DIR"
echo "   ChromaDB: $CHROMADB_PATH"
echo "   Indexer: $INDEXER_SCRIPT"
echo ""

# Check dependencies
echo -e "${BLUE}📦 Verificando dependencias...${NC}"

if ! python3 -c "import chromadb" 2>/dev/null; then
    echo -e "${RED}❌ ChromaDB no instalado${NC}"
    echo "   Instalando dependencias..."
    cd "$BACKEND_DIR"
    pip install chromadb sentence-transformers tqdm
fi

if ! python3 -c "import sentence_transformers" 2>/dev/null; then
    echo -e "${RED}❌ Sentence-Transformers no instalado${NC}"
    echo "   Instalando..."
    pip install sentence-transformers
fi

if ! python3 -c "import tqdm" 2>/dev/null; then
    echo -e "${RED}❌ tqdm no instalado${NC}"
    pip install tqdm
fi

echo -e "${GREEN}✅ Dependencias verificadas${NC}"
echo ""

# Find knowledge sources
echo -e "${BLUE}🔍 Buscando fuentes de conocimiento...${NC}"

declare -a FOUND_SOURCES=()

for source in "${KNOWLEDGE_SOURCES[@]}"; do
    if [ -d "$source" ]; then
        file_count=$(find "$source" -type f \( -name "*.md" -o -name "*.txt" -o -name "*.pdf" \) 2>/dev/null | wc -l | xargs)
        if [ "$file_count" -gt 0 ]; then
            echo -e "   ${GREEN}✅ $source${NC} ($file_count archivos)"
            FOUND_SOURCES+=("$source")
        fi
    fi
done

if [ ${#FOUND_SOURCES[@]} -eq 0 ]; then
    echo -e "${YELLOW} ⚠️  No se encontraron fuentes de conocimiento${NC}"
    echo ""
    echo "Por favor, especifica el directorio con los archivos:"
    read -p "Directorio: " CUSTOM_SOURCE
    
    if [ -d "$CUSTOM_SOURCE" ]; then
        FOUND_SOURCES+=("$CUSTOM_SOURCE")
    else
        echo -e "${RED}❌ Directorio no válido${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}📊 Resumen:${NC}"
echo "   Fuentes encontradas: ${#FOUND_SOURCES[@]}"
for source in "${FOUND_SOURCES[@]}"; do
    echo "   - $source"
done
echo ""

# Confirm
echo -e "${YELLOW}⚠️  IMPORTANTE:${NC}"
echo "   Esta operación indexará TODOS los archivos encontrados"
echo "   Esto puede tardar varios minutos dependiendo del volumen"
echo ""
read -p "¿Continuar con la indexación? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "Cancelado por el usuario"
    exit 0
fi

# Run indexation
echo ""
echo "======================================================================"
echo "  INICIANDO INDEXACIÓN"
echo "======================================================================"
echo ""

for source in "${FOUND_SOURCES[@]}"; do
    echo -e "${BLUE}📥 Indexando: $source${NC}"
    echo ""
    
    python3 "$INDEXER_SCRIPT" \
        --source "$source" \
        --chromadb-path "$CHROMADB_PATH" \
        --test-query "EASA Part-66 supervisor signature requirements"
    
    echo ""
done

echo ""
echo "======================================================================"
echo "  ${GREEN}✅ CEREBRO TRIDENTE ACTIVADO${NC}"
echo "======================================================================"
echo ""
echo "📊 ChromaDB listo en: $CHROMADB_PATH"
echo ""
echo "🧠 El sistema RAG está procesando:"
echo "   - Estándares OJT"
echo "   - Requisitos de Auditoría"
echo "   - Protocolos SMS"
echo "   - Regulaciones EASA/FAA/ICAO/UK CAA/LAR"
echo ""
echo "🚀 Puedes iniciar el servidor ahora con:"
echo "   cd $BACKEND_DIR && python server.py"
echo ""
