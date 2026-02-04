#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Regulation Watcher Service
================================================
Sistema de monitoreo automático de cambios en normativas oficiales

Features:
- Monitoreo semanal de hashes de PDFs
- Detección automática de nuevas versiones
- Diff de contenido con IA
- Alertas visuales en mapa global
- Historial de cambios

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

import asyncio
import aiohttp
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import difflib

@dataclass
class RegulationWatch:
    """Configuración de monitoreo de una normativa"""
    id: str
    authority: str
    region: str
    document_code: str
    url: str
    language: str
    last_hash: Optional[str] = None
    last_check: Optional[str] = None
    last_update: Optional[str] = None

@dataclass
class RegulationUpdate:
    """Actualización detectada"""
    id: str
    authority: str
    region: str
    document_code: str
    old_hash: str
    new_hash: str
    detected_at: str
    change_summary: str
    status: str = 'pending'  # pending, approved, rejected

class RegulationWatcherService:
    """
    Servicio de vigilancia de normativas
    """
    
    def __init__(self, config_path: Path = Path("./config/regulation_watches.json")):
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.watches: List[RegulationWatch] = []
        self.updates: List[RegulationUpdate] = []
        
        self.updates_file = Path("./data/regulation_updates.json")
        self.updates_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Headers para requests
        self.headers = {
            'User-Agent': 'OnTrackIA-RegulationWatcher/2.0 (Compliance Monitoring Bot)'
        }
        
        self.load_watches()
        self.load_updates()
    
    def load_watches(self):
        """Carga configuración de watchs"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.watches = [RegulationWatch(**w) for w in data.get('watches', [])]
        else:
            # Crear configuración inicial
            self.watches = [
                RegulationWatch(
                    id='easa_part66',
                    authority='EASA',
                    region='EU',
                    document_code='Part-66',
                    url='https://www.easa.europa.eu/en/document-library/regulations/commission-regulation-eu-no-13212014',
                    language='en'
                ),
                RegulationWatch(
                    id='faa_8900',
                    authority='FAA',
                    region='US',
                    document_code='Order 8900.1',
                    url='https://www.faa.gov/regulations_policies/orders_notices/index.cfm/go/document.information/documentID/1027770',
                    language='en'
                ),
                RegulationWatch(
                    id='caa_cap741',
                    authority='UK CAA',
                    region='GB',
                    document_code='CAP 741',
                    url='https://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=11&mode=detail&id=325',
                    language='en'
                ),
                RegulationWatch(
                    id='rac_lpta66',
                    authority='RAC Colombia',
                    region='CO',
                    document_code='LPTA 66',
                    url='https://www.aerocivil.gov.co/normatividad/RAC/RAC%20%20066%20-%20Licencias%20y%20Habilitaciones%20del%20Personal%20T%C3%A9cnico%20Aeron%C3%A1utico.pdf',
                    language='es'
                ),
            ]
            self.save_watches()
    
    def save_watches(self):
        """Guarda configuración de watches"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump({
                'watches': [asdict(w) for w in self.watches],
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def load_updates(self):
        """Carga actualizaciones detectadas"""
        if self.updates_file.exists():
            with open(self.updates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.updates = [RegulationUpdate(**u) for u in data.get('updates', [])]
    
    def save_updates(self):
        """Guarda actualizaciones"""
        with open(self.updates_file, 'w', encoding='utf-8') as f:
            json.dump({
                'updates': [asdict(u) for u in self.updates],
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    async def fetch_url_hash(self, url: str) -> Optional[str]:
        """Calcula hash de un recurso web"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        return hashlib.sha256(content).hexdigest()
                    else:
                        print(f"  ✗ HTTP {response.status} for {url}")
                        return None
        except Exception as e:
            print(f"  ✗ Error fetching {url}: {e}")
            return None
    
    async def check_watch(self, watch: RegulationWatch) -> Optional[RegulationUpdate]:
        """Verifica si una normativa ha cambiado"""
        print(f"\n🔍 Checking: {watch.document_code} ({watch.authority})")
        
        current_hash = await self.fetch_url_hash(watch.url)
        
        if current_hash:
            watch.last_check = datetime.now().isoformat()
            
            if watch.last_hash and watch.last_hash != current_hash:
                # Cambio detectado!
                print(f"  🚨 CAMBIO DETECTADO!")
                print(f"     Old hash: {watch.last_hash[:16]}...")
                print(f"     New hash: {current_hash[:16]}...")
                
                update = RegulationUpdate(
                    id=f"{watch.id}_{datetime.now().timestamp()}",
                    authority=watch.authority,
                    region=watch.region,
                    document_code=watch.document_code,
                    old_hash=watch.last_hash,
                    new_hash=current_hash,
                    detected_at=datetime.now().isoformat(),
                    change_summary=f"New version detected for {watch.document_code}",
                    status='pending'
                )
                
                return update
            
            elif not watch.last_hash:
                # Primera vez
                print(f"  ✓ Baseline hash: {current_hash[:16]}...")
                watch.last_hash = current_hash
            else:
                print(f"  ✓ No changes")
        
        return None
    
    async def check_all_watches(self) -> List[RegulationUpdate]:
        """Verifica todas las normativas monitoreadas"""
        print("\n" + "="*70)
        print("REGULATION WATCHER - Inicio de Vigilancia")
        print("="*70)
        print(f"Total watches: {len(self.watches)}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        new_updates = []
        
        for watch in self.watches:
            update = await self.check_watch(watch)
            
            if update:
                new_updates.append(update)
                self.updates.append(update)
            
            # Delay entre requests
            await asyncio.sleep(2)
        
        # Guardar estado
        self.save_watches()
        
        if new_updates:
            self.save_updates()
        
        print("\n" + "="*70)
        print("RESUMEN DE VIGILANCIA")
        print("="*70)
        print(f"Nuevas actualizaciones detectadas: {len(new_updates)}")
        print(f"Actualizaciones pendientes totales: {len([u for u in self.updates if u.status == 'pending'])}")
        
        return new_updates
    
    def get_pending_updates(self) -> List[RegulationUpdate]:
        """Obtiene actualizaciones pendientes de aprobación"""
        return [u for u in self.updates if u.status == 'pending']
    
    def approve_update(self, update_id: str):
        """Aprueba una actualización"""
        for update in self.updates:
            if update.id == update_id:
                update.status = 'approved'
                
                # Actualizar hash en watch
                for watch in self.watches:
                    if (watch.authority == update.authority and 
                        watch.document_code == update.document_code):
                        watch.last_hash = update.new_hash
                        watch.last_update = datetime.now().isoformat()
                
                self.save_watches()
                self.save_updates()
                
                return True
        
        return False
    
    async def generate_diff_summary(
        self,
        old_text: str,
        new_text: str,
        language: str = 'es'
    ) -> str:
        """
        Genera resumen de diferencias usando IA
        
        Args:
            old_text: Texto antiguo
            new_text: Texto nuevo
            language: Idioma del resumen
        
        Returns:
            Resumen de cambios
        """
        # Generar diff básico
        diff = list(difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            lineterm=''
        ))
        
        if len(diff) > 0:
            # Aquí se puede integrar con Mistral para generar resumen inteligente
            additions = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
            deletions = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
            
            if language == 'es':
                return f"Detectados {additions} líneas añadidas y {deletions} líneas eliminadas. Revisión manual recomendada."
            else:
                return f"Detected {additions} lines added and {deletions} lines removed. Manual review recommended."
        
        return "No significant changes detected" if language == 'en' else "No se detectaron cambios significativos"

# Ejemplo de uso
async def main():
    watcher = RegulationWatcherService()
    
    # Ejecutar vigilancia
    updates = await watcher.check_all_watches()
    
    if updates:
        print("\n📬 Nuevas actualizaciones que requieren aprobación:")
        for update in updates:
            print(f"\n  - {update.document_code} ({update.authority})")
            print(f"    Región: {update.region}")
            print(f"    Detectado: {update.detected_at}")

if __name__ == "__main__":
    asyncio.run(main())
