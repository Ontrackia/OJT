#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - FastAPI Main Server
=========================================
Servidor principal con todos los routers

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import routers
from app.routers import ojt, rag, interview, visual_scan, audit_v2

# Create FastAPI app
app = FastAPI(
    title="OnTrackIA OJT V2.0 API",
    description="Sistema de Gestión OJT con RAG Multi-Agente",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configurar orígenes específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (uploads)
uploads_dir = Path("./uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Include routers
app.include_router(ojt.router)
app.include_router(rag.router)
app.include_router(interview.router)
app.include_router(visual_scan.router)
app.include_router(audit_v2.router)  # 🆕 Dashboard Auditor V2

@app.get("/")
async def root():
    return {
        "service": "OnTrackIA OJT V2.0",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Visual Scan with Forensic Integrity",
            "Image Optimization (5MB → 400KB)",
            "Senior Auditor Coach (RAG Multi-Agent)",
            "Dashboard Auditor V2.0",
            "Global Regulatory Surveillance",
            "Critical Interview Protocol"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
