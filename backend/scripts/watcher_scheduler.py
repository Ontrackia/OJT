#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Regulation Watcher Scheduler
==================================================
Programador de tareas para vigilancia semanal de normativas

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
"""

import asyncio
import schedule
import time
from datetime import datetime
from pathlib import Path
import sys

# Agregar path de scripts
sys.path.append(str(Path(__file__).parent))

from regulation_watcher import RegulationWatcherService

class WatcherScheduler:
    """
    Programador de vigilancia de normativas
    """
    
    def __init__(self):
        self.watcher = RegulationWatcherService()
        self.running = False
    
    async def run_watch_cycle(self):
        """Ejecuta un ciclo de vigilancia"""
        print(f"\n{'='*70}")
        print(f"🔔 Iniciando ciclo de vigilancia programado")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*70}\n")
        
        try:
            updates = await self.watcher.check_all_watches()
            
            if updates:
                print(f"\n📬 {len(updates)} actualizaciones detectadas")
                print("   Requieren aprobación en el dashboard")
            else:
                print("\n✓ No se detectaron actualizaciones")
        
        except Exception as e:
            print(f"\n✗ Error en ciclo de vigilancia: {e}")
    
    def schedule_weekly_watch(self):
        """Programa vigilancia semanal (todos los lunes a las 03:00)"""
        schedule.every().monday.at("03:00").do(
            lambda: asyncio.run(self.run_watch_cycle())
        )
        
        print("✓ Vigilancia programada: Lunes 03:00 AM")
    
    def schedule_daily_watch(self):
        """Programa vigilancia diaria (a las 03:00)"""
        schedule.every().day.at("03:00").do(
            lambda: asyncio.run(self.run_watch_cycle())
        )
        
        print("✓ Vigilancia programada: Diario 03:00 AM")
    
    def run_scheduler(self):
        """Inicia el scheduler"""
        self.running = True
        
        print("\n" + "="*70)
        print("REGULATION WATCHER SCHEDULER")
        print("="*70)
        print(f"Inicio: {datetime.now().isoformat()}")
        print(f"Modo: Vigilancia Semanal")
        print("="*70 + "\n")
        
        # Programar vigilancia semanal
        self.schedule_weekly_watch()
        
        # También ejecutar inmediatamente al inicio
        print("Ejecutando vigilancia inicial...")
        asyncio.run(self.run_watch_cycle())
        
        print("\n💤 Scheduler en espera de próximo ciclo...\n")
        
        # Loop infinito
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check cada minuto
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler detenido manualmente")
            self.running = False

if __name__ == "__main__":
    scheduler = WatcherScheduler()
    scheduler.run_scheduler()
