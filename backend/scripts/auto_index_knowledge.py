#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Auto Knowledge Indexer
============================================
Indexa automáticamente nuevos archivos .md en RAG durante deployment

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Agregar path de scripts
sys.path.append(str(Path(__file__).parent))

from rag_indexing import RAGIndexingService

class AutoKnowledgeIndexer:
    """
    Indexador automático de archivos de conocimiento
    """
    
    def __init__(self):
        self.rag = RAGIndexingService()
        self.knowledge_dir = Path("./docs/knowledge_item")
        self.index_log = Path("./data/index_log.json")
        
        # Cargar log de indexación
        self.indexed_files = self._load_index_log()
    
    def _load_index_log(self) -> dict:
        """Carga registro de archivos indexados"""
        if self.index_log.exists():
            with open(self.index_log, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index_log(self):
        """Guarda registro de archivos indexados"""
        self.index_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_log, 'w', encoding='utf-8') as f:
            json.dump(self.indexed_files, f, indent=2)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Calcula hash del archivo"""
        import hashlib
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _is_indexed(self, file_path: Path) -> bool:
        """Verifica si el archivo ya fue indexado"""
        file_key = str(file_path.relative_to(self.knowledge_dir))
        
        if file_key in self.indexed_files:
            # Verificar si cambió
            current_hash = self._get_file_hash(file_path)
            stored_hash = self.indexed_files[file_key].get('hash')
            
            return current_hash == stored_hash
        
        return False
    
    def auto_index_new_files(self):
        """Indexa automáticamente archivos nuevos o modificados"""
        print("\n" + "="*70)
        print("AUTO KNOWLEDGE INDEXER - OnTrackIA OJT V2.0")
        print("="*70)
        print(f"Knowledge directory: {self.knowledge_dir}")
        
        if not self.knowledge_dir.exists():
            print("⚠️  Knowledge directory not found")
            return
        
        # Buscar archivos .md
        md_files = list(self.knowledge_dir.rglob("*.md"))
        
        if not md_files:
            print("📭 No markdown files found")
            return
        
        print(f"📂 Found {len(md_files)} markdown files")
        
        indexed_count = 0
        skipped_count = 0
        
        for md_file in md_files:
            file_key = str(md_file.relative_to(self.knowledge_dir))
            
            if self._is_indexed(md_file):
                print(f"⏭️  {file_key} (already indexed)")
                skipped_count += 1
                continue
            
            print(f"\n📝 Indexing: {file_key}")
            
            try:
                # Indexar en ChromaDB
                chunk_count = self.rag.index_markdown_file(md_file)
                
                # Guardar en log
                file_hash = self._get_file_hash(md_file)
                self.indexed_files[file_key] = {
                    'hash': file_hash,
                    'chunks': chunk_count,
                    'indexed_at': datetime.now().isoformat()
                }
                
                print(f"   ✓ Indexed {chunk_count} chunks")
                indexed_count += 1
            
            except Exception as e:
                print(f"   ✗ Error: {e}")
        
        # Guardar log
        if indexed_count > 0:
            self._save_index_log()
        
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print(f"✓ Indexed: {indexed_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        print(f"📊 Total: {len(md_files)}")
        print("="*70 + "\n")

if __name__ == "__main__":
    try:
        indexer = AutoKnowledgeIndexer()
        indexer.auto_index_new_files()
    except Exception as e:
        print(f"\n❌ Auto-indexing failed: {e}")
        exit(1)
