#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Database Migration Script
===============================================
Aplica migraciones automáticamente durante deployment

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

import psycopg2
from psycopg2 import sql
import hashlib
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MigrationRunner:
    """
    Gestor de migraciones de base de datos
    """
    
    def __init__(self):
        # Conexión a PostgreSQL
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            database=os.getenv('POSTGRES_DB', 'ontrackia_ojt'),
            user=os.getenv('POSTGRES_USER', 'ontrackia'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        self.cursor = self.conn.cursor()
        
        # Directorio de migraciones
        self.migrations_dir = Path(__file__).parent.parent / 'database' / 'migrations'
        
        # Crear tabla de historial si no existe
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Crea tabla de control de migraciones"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                file_hash VARCHAR(64) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calcula hash SHA-256 del archivo SQL"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _is_applied(self, filename: str, file_hash: str) -> bool:
        """Verifica si la migración ya fue aplicada"""
        self.cursor.execute(
            "SELECT file_hash FROM _migrations WHERE filename = %s",
            (filename,)
        )
        result = self.cursor.fetchone()
        
        if result:
            # Migración existe, verificar si cambió
            return result[0] == file_hash
        
        return False
    
    def _mark_as_applied(self, filename: str, file_hash: str):
        """Marca migración como aplicada"""
        self.cursor.execute("""
            INSERT INTO _migrations (filename, file_hash)
            VALUES (%s, %s)
            ON CONFLICT (filename) 
            DO UPDATE SET file_hash = EXCLUDED.file_hash, 
                         applied_at = CURRENT_TIMESTAMP
        """, (filename, file_hash))
        self.conn.commit()
    
    def run_migrations(self):
        """Ejecuta todas las migraciones pendientes"""
        print("\n" + "="*70)
        print("DATABASE MIGRATIONS - OnTrackIA OJT V2.0")
        print("="*70)
        
        if not self.migrations_dir.exists():
            print("⚠️  No migrations directory found")
            return
        
        # Obtener archivos SQL ordenados
        sql_files = sorted(self.migrations_dir.glob("*.sql"))
        
        if not sql_files:
            print("📭 No migration files found")
            return
        
        applied_count = 0
        skipped_count = 0
        
        for sql_file in sql_files:
            filename = sql_file.name
            file_hash = self._calculate_file_hash(sql_file)
            
            if self._is_applied(filename, file_hash):
                print(f"⏭️  {filename} (already applied)")
                skipped_count += 1
                continue
            
            print(f"\n📝 Applying: {filename}")
            
            try:
                # Leer y ejecutar SQL
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                self.cursor.execute(sql_content)
                self.conn.commit()
                
                # Marcar como aplicada
                self._mark_as_applied(filename, file_hash)
                
                print(f"   ✓ Applied successfully")
                applied_count += 1
            
            except Exception as e:
                print(f"   ✗ Error: {e}")
                self.conn.rollback()
                raise
        
        print("\n" + "="*70)
        print(f"SUMMARY")
        print("="*70)
        print(f"✓ Applied: {applied_count}")
        print(f"⏭️  Skipped: {skipped_count}")
        print(f"📊 Total: {len(sql_files)}")
        print("="*70 + "\n")
    
    def close(self):
        """Cierra conexión"""
        self.cursor.close()
        self.conn.close()

if __name__ == "__main__":
    try:
        runner = MigrationRunner()
        runner.run_migrations()
        runner.close()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        exit(1)
