#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - RAG API Endpoints
=======================================
Endpoints para upload, conversión e indexación de normativas

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
from typing import List, Dict
from pydantic import BaseModel

# Importar servicios RAG
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'scripts'))

from pdf_to_markdown import PDFToMarkdownConverter
from rag_indexing import RAGIndexingService

router = APIRouter()

# Directorios
PDF_UPLOAD_DIR = Path("./uploads/pdfs")
MARKDOWN_DIR = Path("./docs/knowledge_item")

# Crear directorios si no existen
PDF_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)

class ConvertRequest(BaseModel):
    filename: str

class IndexRequest(BaseModel):
    filename: str

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Upload de archivo PDF normativo
    
    Args:
        file: Archivo PDF
    
    Returns:
        Confirmación de upload
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Guardar archivo
    file_path = PDF_UPLOAD_DIR / file.filename
    
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file.file, f)
    
    return {
        "status": "uploaded",
        "filename": file.filename,
        "path": str(file_path)
    }

@router.post("/convert")
async def convert_pdf_to_markdown(request: ConvertRequest):
    """
    Convierte PDF a Markdown
    
    Args:
        request: Filename del PDF
    
    Returns:
        Confirmación de conversión
    """
    pdf_path = PDF_UPLOAD_DIR / request.filename
    
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Convertir
    converter = PDFToMarkdownConverter()
    md_path = converter.convert_pdf_to_markdown(pdf_path, MARKDOWN_DIR)
    
    return {
        "status": "converted",
        "pdf_file": request.filename,
        "markdown_file": md_path.name,
        "markdown_path": str(md_path)
    }

@router.post("/index")
async def index_markdown(request: IndexRequest):
    """
    Indexa archivo Markdown en ChromaDB
    
    Args:
        request: Filename del Markdown
    
    Returns:
        Confirmación de indexación con cantidad de chunks
    """
    md_path = MARKDOWN_DIR / request.filename
    
    if not md_path.exists():
        raise HTTPException(status_code=404, detail="Markdown file not found")
    
    # Indexar
    rag = RAGIndexingService()
    chunk_count = rag.index_markdown_file(md_path)
    
    # Calcular hash
    import hashlib
    with open(md_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    return {
        "status": "indexed",
        "filename": request.filename,
        "chunk_count": chunk_count,
        "file_hash": file_hash
    }

@router.get("/documents")
async def get_indexed_documents():
    """
    Obtiene lista de documentos indexados
    
    Returns:
        Lista de documentos con metadata
    """
    documents = []
    
    for md_file in MARKDOWN_DIR.glob("*.md"):
        # Leer metadatos del archivo
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]
        
        metadata = {
            'document_code': md_file.stem,
            'authority': 'Unknown',
            'chunk_count': 0,
            'language': 'en',
            'update_date': '2026-02-04'
        }
        
        for line in lines:
            if '**Autoridad:**' in line:
                metadata['authority'] = line.split('**Autoridad:**')[1].strip()
            elif '**Fecha:**' in line:
                metadata['update_date'] = line.split('**Fecha:**')[1].strip()
            elif '**Idioma:**' in line:
                metadata['language'] = line.split('**Idioma:**')[1].strip()
        
        documents.append(metadata)
    
    return {"documents": documents}

@router.post("/search")
async def search_rag(query: str, n_results: int = 5, language: str = None):
    """
    Búsqueda semántica en base de conocimiento RAG
    
    Args:
        query: Consulta en lenguaje natural
        n_results: Número de resultados
        language: Filtrar por idioma (opcional)
    
    Returns:
        Chunks relevantes
    """
    rag = RAGIndexingService()
    
    results = rag.search(
        query=query,
        n_results=n_results,
        filter_language=language
    )
    
    return {
        "query": query,
        "results_count": len(results),
        "results": results
    }

@router.get("/coverage")
async def get_global_coverage():
    """
    Obtiene cobertura normativa global para el mapa
    
    Returns:
        Coverage data por región
    """
    coverage = {}
    
    # Analizar archivos markdown en world_regs
    world_regs_dir = Path("./docs/knowledge_item/world_regs")
    
    if world_regs_dir.exists():
        for md_file in world_regs_dir.glob("*.md"):
            # Extraer metadata
            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:20]
            
            authority = None
            document_code = None
            language = 'en'
            update_date = '2026-02-04'
            
            for line in lines:
                if '**Autoridad:**' in line or '**Authority:**' in line:
                    authority = line.split('**')[2].strip()
                elif '**Código:**' in line or '**Code:**' in line:
                    document_code = line.split('**')[2].strip()
                elif '**Idioma:**' in line or '**Language:**' in line:
                    language = line.split('**')[2].strip()
                elif '**Fecha:**' in line or '**Date:**' in line:
                    update_date = line.split('**')[2].strip()
            
            # Determinar región
            filename = md_file.stem.lower()
            if 'easa' in filename:
                region = 'EU'
            elif 'faa' in filename:
                region = 'US'
            elif 'caa' in filename or 'uk' in filename:
                region = 'GB'
            elif 'rac' in filename or 'colombia' in filename:
                region = 'CO'
            elif 'mexico' in filename or 'dgac' in filename:
                region = 'MX'
            else:
                region = 'ICAO'
            
            if region not in coverage:
                coverage[region] = {
                    'authority': authority or 'Unknown',
                    'documents': 0,
                    'regulations': []
                }
            
            coverage[region]['documents'] += 1
            coverage[region]['regulations'].append({
                'document_code': document_code or md_file.stem,
                'language': language,
                'update_date': update_date
            })
    
    return {"coverage": coverage}

@router.get("/pending-updates")
async def get_pending_updates():
    """
    Obtiene actualizaciones normativas pendientes de aprobación
    
    Returns:
        Lista de actualizaciones pendientes
    """
    import sys
    sys_path_parent = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.append(str(sys_path_parent))
    
    try:
        from regulation_watcher import RegulationWatcherService
        
        watcher = RegulationWatcherService()
        pending = watcher.get_pending_updates()
        
        return {
            "updates": [
                {
                    "id": u.id,
                    "authority": u.authority,
                    "region": u.region,
                    "document_code": u.document_code,
                    "detected_at": u.detected_at,
                    "change_summary": u.change_summary,
                    "status": u.status
                }
                for u in pending
            ]
        }
    except Exception as e:
        return {"updates": [], "error": str(e)}

@router.post("/approve-update/{update_id}")
async def approve_regulation_update(update_id: str):
    """
    Aprueba una actualización normativa para indexación
    
    Args:
        update_id: ID de la actualización
    
    Returns:
        Confirmación de aprobación
    """
    import sys
    sys_path_parent = Path(__file__).parent.parent.parent / 'scripts'
    sys.path.append(str(sys_path_parent))
    
    try:
        from regulation_watcher import RegulationWatcherService
        
        watcher = RegulationWatcherService()
        
        if watcher.approve_update(update_id):
            return {
                "status": "approved",
                "update_id": update_id,
                "message": "Update approved and ready for indexing"
            }
        else:
            raise HTTPException(status_code=404, detail="Update not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
