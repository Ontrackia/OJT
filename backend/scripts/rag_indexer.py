#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - RAG Knowledge Base Indexer
================================================
Sistema de indexación masiva para ChromaDB
Carga 865 archivos + normativa mundial (EASA/FAA/ICAO/UK CAA)

CEREBRO TRIDENTE: OJT + Audit + SMS

@author OnTrackia Dev Team
@date 2026-02-04
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import hashlib
import json
from datetime import datetime

# ChromaDB & Embeddings
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Document processing
from tqdm import tqdm

class RAGKnowledgeIndexer:
    """
    Indexador de conocimiento para el sistema RAG
    """
    
    # Document categories (para lógica transversal)
    CATEGORIES = {
        'OJT_STANDARD': 'Estándar OJT',
        'AUDIT_REQUIREMENT': 'Requisito de Auditoría',
        'SMS_PROTOCOL': 'Protocolo SMS',
        'EASA_REGULATION': 'Regulación EASA',
        'FAA_REGULATION': 'Regulación FAA',
        'ICAO_STANDARD': 'Estándar ICAO',
        'UK_CAA_REGULATION': 'Regulación UK CAA',
        'LAR_REGULATION': 'Regulación LAR',
        'MAINTENANCE_MANUAL': 'Manual de Mantenimiento',
        'TECHNICAL_DOC': 'Documentación Técnica'
    }
    
    def __init__(self, chromadb_path: str = "./data/chromadb"):
        """
        Initialize RAG indexer
        
        Args:
            chromadb_path: Path to ChromaDB persistent storage
        """
        print("=" * 70)
        print("ONTRACKIA OJT V2.0 - RAG KNOWLEDGE BASE INDEXER")
        print("=" * 70)
        print(f"Inicializando ChromaDB en: {chromadb_path}")
        
        # Create directory
        Path(chromadb_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=chromadb_path
        ))
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="ontrackia_knowledge",
            metadata={
                "description": "OnTrackIA OJT V2.0 - Cerebro Tridente (OJT + Audit + SMS)",
                "version": "2.0",
                "created_at": datetime.now().isoformat()
            }
        )
        
        print(f"✅ Collection 'ontrackia_knowledge' creada/cargada")
        print(f"   Documentos actuales: {self.collection.count()}")
        
        # Initialize embedding model
        print("\n🧠 Cargando modelo de embeddings...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Modelo cargado: all-MiniLM-L6-v2 (384 dim)")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for block in iter(lambda: f.read(4096), b''):
                sha256.update(block)
        return sha256.hexdigest()
    
    def _extract_markdown_metadata(self, content: str) -> tuple[str, Dict]:
        """
        Extraer metadata YAML de Markdown frontmatter
        
        Returns:
            (content_without_frontmatter, metadata_dict)
        """
        import re
        
        # Check for YAML frontmatter (---\n...\n---)
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if not match:
            return content, {}
        
        frontmatter = match.group(1)
        content_without_frontmatter = content[match.end():]
        
        # Parse YAML manually (simple key: value pairs)
        metadata = {}
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
        
        return content_without_frontmatter, metadata
    
    def _detect_category(self, file_path: Path, content: str, frontmatter_meta: Dict = None) -> str:
        """
        Detectar categoría del documento basado en path y contenido
        """
        path_str = str(file_path).lower()
        content_lower = content.lower()
        
        # EASA
        if 'easa' in path_str or 'part-145' in path_str or 'part-66' in path_str:
            return 'EASA_REGULATION'
        
        # FAA
        if 'faa' in path_str or 'far' in path_str or '8900.1' in path_str:
            return 'FAA_REGULATION'
        
        # ICAO
        if 'icao' in path_str or 'annex' in path_str:
            return 'ICAO_STANDARD'
        
        # UK CAA
        if 'uk caa' in path_str or 'cap' in path_str:
            return 'UK_CAA_REGULATION'
        
        # LAR
        if 'lar' in path_str:
            return 'LAR_REGULATION'
        
        # OJT
        if 'ojt' in path_str or 'training' in path_str:
            return 'OJT_STANDARD'
        
        # Audit
        if 'audit' in path_str or 'compliance' in path_str:
            return 'AUDIT_REQUIREMENT'
        
        # SMS
        if 'sms' in path_str or 'safety' in path_str:
            return 'SMS_PROTOCOL'
        
        # Maintenance manuals
        if 'amm' in path_str or 'manual' in path_str or 'maintenance' in path_str:
            return 'MAINTENANCE_MANUAL'
        
        # Default
        return 'TECHNICAL_DOC'
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Dividir texto en chunks con overlap
        """
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        return chunks
    
    def index_directory(
        self,
        source_dir: str,
        extensions: List[str] = ['.md', '.txt', '.pdf'],
        clear_existing: bool = False
    ) -> Dict:
        """
        Indexar todos los archivos de un directorio
        
        Args:
            source_dir: Directorio source
            extensions: Extensiones de archivo a indexar
            clear_existing: Si True, borra la collection antes de indexar
        
        Returns:
            Estadísticas de indexación
        """
        print("\n" + "=" * 70)
        print(f"INDEXANDO DIRECTORIO: {source_dir}")
        print("=" * 70)
        
        if clear_existing:
            print("⚠️  BORRANDO COLLECTION EXISTENTE...")
            self.chroma_client.delete_collection("ontrackia_knowledge")
            self.collection = self.chroma_client.create_collection(
                name="ontrackia_knowledge",
                metadata={
                    "description": "OnTrackIA OJT V2.0 - Cerebro Tridente",
                    "version": "2.0",
                    "created_at": datetime.now().isoformat()
                }
            )
            print("✅ Collection reiniciada")
        
        # Find all files
        source_path = Path(source_dir)
        all_files = []
        
        for ext in extensions:
            all_files.extend(source_path.rglob(f'*{ext}'))
        
        print(f"\n📁 Archivos encontrados: {len(all_files)}")
        
        if len(all_files) == 0:
            print("❌ No se encontraron archivos para indexar")
            return {}
        
        # Statistics
        stats = {
            'total_files': len(all_files),
            'indexed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'categories': {}
        }
        
        # Process each file
        print("\n🔄 Procesando archivos...\n")
        
        for file_path in tqdm(all_files, desc="Indexando"):
            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                if not content.strip():
                    continue
                
                # Extract frontmatter metadata (YAML) if exists
                frontmatter_meta = {}
                if file_path.suffix == '.md':
                    content, frontmatter_meta = self._extract_markdown_metadata(content)
                
                # Calculate hash
                file_hash = self._calculate_file_hash(file_path)
                
                # Detect category (puede usar frontmatter)
                category = self._detect_category(file_path, content, frontmatter_meta)
                
                # Update category stats
                if category not in stats['categories']:
                    stats['categories'][category] = 0
                stats['categories'][category] += 1
                
                # Chunk text
                chunks = self._chunk_text(content)
                
                # Generate embeddings and add to collection
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{file_hash}_{i}"
                    
                    # Generate embedding
                    embedding = self.embedding_model.encode(chunk).tolist()
                    
                    # Build metadata (combina frontmatter + detección)
                    chunk_metadata = {
                        'source_file': str(file_path),
                        'file_name': file_path.name,
                        'category': category,
                        'category_label': self.CATEGORIES.get(category, 'Unknown'),
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'file_hash': file_hash,
                        'indexed_at': datetime.now().isoformat()
                    }
                    
                    # Add frontmatter fields (territory, authority, etc)
                    if frontmatter_meta:
                        chunk_metadata['territory'] = frontmatter_meta.get('territory', 'GLOBAL')
                        chunk_metadata['authority'] = frontmatter_meta.get('authority', '')
                        chunk_metadata['abbreviation'] = frontmatter_meta.get('abbreviation', '')
                        chunk_metadata['document_type'] = frontmatter_meta.get('document_type', '')
                    else:
                        chunk_metadata['territory'] = 'GLOBAL'
                    
                    # Add to ChromaDB
                    self.collection.add(
                        ids=[chunk_id],
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[chunk_metadata]
                    )
                
                stats['indexed_files'] += 1
                stats['total_chunks'] += len(chunks)
                
            except Exception as e:
                print(f"\n❌ Error procesando {file_path}: {e}")
                stats['failed_files'] += 1
        
        # Persist changes
        self.chroma_client.persist()
        
        # Print final stats
        print("\n" + "=" * 70)
        print("INDEXACIÓN COMPLETADA")
        print("=" * 70)
        print(f"✅ Archivos indexados: {stats['indexed_files']}/{stats['total_files']}")
        print(f"❌ Archivos fallidos: {stats['failed_files']}")
        print(f"📦 Total chunks: {stats['total_chunks']}")
        print(f"💾 Documentos en ChromaDB: {self.collection.count()}")
        
        print("\n📊 DISTRIBUCIÓN POR CATEGORÍA:")
        for cat, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            label = self.CATEGORIES.get(cat, cat)
            print(f"   {label:30s}: {count:4d} archivos")
        
        return stats
    
    def search(self, query: str, n_results: int = 10, category_filter: str = None) -> Dict:
        """
        Buscar en la base de conocimientos
        
        Args:
            query: Texto de búsqueda
            n_results: Número de resultados
            category_filter: Filtrar por categoría (opcional)
        
        Returns:
            Resultados de búsqueda
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Build filter
        where_filter = None
        if category_filter:
            where_filter = {"category": category_filter}
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_filter
        )
        
        return results
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas de la collection"""
        total = self.collection.count()
        
        # Get sample to analyze categories
        if total > 0:
            sample = self.collection.get(limit=min(total, 1000))
            categories = {}
            
            for metadata in sample['metadatas']:
                cat = metadata.get('category', 'UNKNOWN')
                categories[cat] = categories.get(cat, 0) + 1
        else:
            categories = {}
        
        return {
            'total_documents': total,
            'categories': categories
        }


def main():
    """
    Main execution
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='OnTrackIA RAG Knowledge Indexer')
    parser.add_argument('--source', type=str, required=True, help='Source directory to index')
    parser.add_argument('--clear', action='store_true', help='Clear existing collection before indexing')
    parser.add_argument('--chromadb-path', type=str, default='./data/chromadb', help='ChromaDB path')
    parser.add_argument('--test-query', type=str, help='Test query after indexing')
    
    args = parser.parse_args()
    
    # Initialize indexer
    indexer = RAGKnowledgeIndexer(chromadb_path=args.chromadb_path)
    
    # Index directory
    stats = indexer.index_directory(
        source_dir=args.source,
        clear_existing=args.clear
    )
    
    # Test query
    if args.test_query:
        print("\n" + "=" * 70)
        print(f"TEST QUERY: {args.test_query}")
        print("=" * 70)
        
        results = indexer.search(args.test_query, n_results=5)
        
        for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            print(f"\n[{i+1}] {metadata['file_name']} ({metadata['category_label']})")
            print(f"    {doc[:200]}...")
    
    print("\n✅ PROCESO COMPLETADO")


if __name__ == "__main__":
    main()
