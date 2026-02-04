#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - RAG Indexing Service
==========================================
Servicio de chunking, vectorización e indexación para RAG

Features:
- Chunking con overlapping 10%
- Vectorización con embeddings
- Indexación en ChromaDB/PGVector
- Búsqueda semántica

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib
import re

@dataclass
class ChunkMetadata:
    """Metadatos de un chunk"""
    source: str
    authority: str
    document_code: str
    chunk_index: int
    total_chunks: int
    criticality_level: str
    language: str
    update_date: str

class RAGIndexingService:
    """
    Servicio de indexación RAG con chunking y vectorización
    """
    
    def __init__(self, collection_name: str = "aviation_regulations"):
        # Inicializar ChromaDB
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./data/chromadb"
        ))
        
        # Obtener o crear colección
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Aviation regulatory documents for RAG"}
        )
        
        print(f"✓ ChromaDB collection '{collection_name}' ready")
    
    def chunk_text(
        self,
        text: str,
        chunk_size: int = 800,
        overlap_percentage: float = 0.10
    ) -> List[str]:
        """
        Divide texto en chunks con overlapping
        
        Args:
            text: Texto a dividir
            chunk_size: Tamaño del chunk en tokens (aprox. palabras)
            overlap_percentage: Porcentaje de solapamiento (0.0 - 1.0)
        
        Returns:
            Lista de chunks
        """
        # Dividir en palabras
        words = text.split()
        
        # Calcular overlap
        overlap_size = int(chunk_size * overlap_percentage)
        step_size = chunk_size - overlap_size
        
        chunks = []
        for i in range(0, len(words), step_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        return chunks
    
    def extract_metadata_from_markdown(self, md_path: Path) -> Dict[str, str]:
        """Extrae metadatos del header del markdown"""
        metadata = {}
        
        with open(md_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:20]  # Primeras 20 líneas
            
            for line in lines:
                if '**Autoridad:**' in line:
                    metadata['authority'] = line.split('**Autoridad:**')[1].strip()
                elif '**Fuente:**' in line:
                    metadata['source'] = line.split('**Fuente:**')[1].strip()
                elif '**Fecha:**' in line:
                    metadata['update_date'] = line.split('**Fecha:**')[1].strip()
                elif '**Nivel de Criticidad:**' in line:
                    metadata['criticality_level'] = line.split('**Nivel de Criticidad:**')[1].strip()
                elif '**Idioma:**' in line:
                    metadata['language'] = line.split('**Idioma:**')[1].strip()
        
        # Intentar extraer document_code del nombre del archivo
        filename = md_path.stem
        if 'part-66' in filename.lower() or 'part_66' in filename.lower():
            metadata['document_code'] = 'Part-66'
        elif 'part-145' in filename.lower():
            metadata['document_code'] = 'Part-145'
        elif 'lpta' in filename.lower():
            metadata['document_code'] = 'LPTA 66'
        elif 'cap' in filename.lower():
            metadata['document_code'] = 'CAP 741'
        else:
            metadata['document_code'] = filename
        
        return metadata
    
    def index_markdown_file(
        self,
        md_path: Path,
        chunk_size: int = 800,
        overlap_percentage: float = 0.10
    ) -> int:
        """
        Indexa un archivo Markdown en ChromaDB
        
        Args:
            md_path: Ruta al archivo Markdown
            chunk_size: Tamaño de chunks
            overlap_percentage: Porcentaje de overlap
        
        Returns:
            Número de chunks indexados
        """
        print(f"\nIndexando: {md_path.name}")
        
        # Leer contenido
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extraer metadata
        base_metadata = self.extract_metadata_from_markdown(md_path)
        print(f"  Documento: {base_metadata.get('document_code', 'Unknown')}")
        print(f"  Autoridad: {base_metadata.get('authority', 'Unknown')}")
        
        # Chunking
        chunks = self.chunk_text(content, chunk_size, overlap_percentage)
        print(f"  Chunks generados: {len(chunks)}")
        
        # Preparar datos para indexación
        chunk_ids = []
        chunk_texts = []
        chunk_metadatas = []
        
        for idx, chunk in enumerate(chunks):
            # ID único del chunk
            chunk_id = hashlib.md5(f"{md_path.name}_{idx}".encode()).hexdigest()
            
            # Metadata del chunk
            metadata = {
                **base_metadata,
                'chunk_index': idx,
                'total_chunks': len(chunks),
                'file_path': str(md_path)
            }
            
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk)
            chunk_metadatas.append(metadata)
        
        # Indexar en ChromaDB
        self.collection.add(
            ids=chunk_ids,
            documents=chunk_texts,
            metadatas=chunk_metadatas
        )
        
        print(f"  ✓ {len(chunks)} chunks indexados en ChromaDB")
        
        return len(chunks)
    
    def index_directory(
        self,
        docs_dir: Path,
        chunk_size: int = 800,
        overlap_percentage: float = 0.10
    ) -> Dict[str, int]:
        """
        Indexa todos los archivos Markdown de un directorio
        
        Args:
            docs_dir: Directorio con archivos .md
            chunk_size: Tamaño de chunks
            overlap_percentage: Overlap
        
        Returns:
            Diccionario con cantidad de chunks por archivo
        """
        results = {}
        
        for md_file in docs_dir.glob("*.md"):
            try:
                chunk_count = self.index_markdown_file(
                    md_file,
                    chunk_size,
                    overlap_percentage
                )
                results[md_file.name] = chunk_count
            except Exception as e:
                print(f"  ✗ Error indexando {md_file.name}: {e}")
                results[md_file.name] = 0
        
        return results
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_authority: Optional[str] = None,
        filter_language: Optional[str] = None
    ) -> List[Dict]:
        """
        Búsqueda semántica en la base de conocimiento
        
        Args:
            query: Consulta en lenguaje natural
            n_results: Número de resultados
            filter_authority: Filtrar por autoridad (EASA, RAC, CAA)
            filter_language: Filtrar por idioma (es, en)
        
        Returns:
            Lista de chunks relevantes
        """
        # Construir filtro
        where_filter = {}
        if filter_authority:
            where_filter['authority'] = filter_authority
        if filter_language:
            where_filter['language'] = filter_language
        
        # Buscar
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter if where_filter else None
        )
        
        # Formatear resultados
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'chunk_id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results

# Ejemplo de uso
if __name__ == "__main__":
    # Crear servicio RAG
    rag = RAGIndexingService()
    
    # Indexar documentos
    docs_dir = Path("./docs/knowledge_item")
    
    if docs_dir.exists():
        print("\n" + "="*70)
        print("INDEXACIÓN RAG - OnTrackIA V2.0")
        print("="*70)
        
        results = rag.index_directory(docs_dir)
        
        print("\n" + "="*70)
        print("RESUMEN DE INDEXACIÓN")
        print("="*70)
        for filename, chunk_count in results.items():
            print(f"  {filename}: {chunk_count} chunks")
        
        print(f"\nTotal chunks indexados: {sum(results.values())}")
        
        # Test de búsqueda
        print("\n" + "="*70)
        print("TEST DE BÚSQUEDA SEMÁNTICA")
        print("="*70)
        
        test_query = "requisitos de experiencia práctica para licencia B1"
        print(f"\nConsulta: '{test_query}'")
        
        search_results = rag.search(test_query, n_results=3)
        
        for idx, result in enumerate(search_results, 1):
            print(f"\n{idx}. {result['metadata'].get('document_code', 'Unknown')}")
            print(f"   Autoridad: {result['metadata'].get('authority', 'Unknown')}")
            print(f"   Relevancia: {1 - result['distance']:.2%}" if result['distance'] else "")
            print(f"   Texto: {result['text'][:200]}...")
    else:
        print(f"Directorio {docs_dir} no encontrado")
        print("Primero ejecuta pdf_to_markdown.py para generar los archivos .md")
