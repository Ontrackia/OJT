#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Global Regulations Scraper
================================================
Web scraper para descarga automática de normativas OJT globales

Fuentes:
- EASA (Part 66, Part 145, AMC/GM)
- FAA (AMT Logbooks, Order 8900.1, AC 65-30)
- UK CAA (CAP 741)
- Latinoamérica (LAR 66, RAC LPTA 66)
- Medio Oriente (GCAA/GACA CAR 66)
- ICAO (Doc 9859, Doc 7192)

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: Solo fuentes oficiales gubernamentales
"""

import requests
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime

@dataclass
class RegulationSource:
    """Fuente de regulación"""
    authority: str
    region: str
    document_code: str
    url: str
    language: str
    criticality: str = 'high'

class GlobalRegulationsScraper:
    """
    Scraper de normativas aeronáuticas globales
    """
    
    # Catálogo de fuentes oficiales
    OFFICIAL_SOURCES = [
        # EASA - Europa
        RegulationSource(
            authority='EASA',
            region='Europe',
            document_code='Part-66',
            url='https://www.easa.europa.eu/en/document-library/regulations/commission-regulation-eu-no-13212014',
            language='en'
        ),
        RegulationSource(
            authority='EASA',
            region='Europe',
            document_code='Part-145',
            url='https://www.easa.europa.eu/en/document-library/regulations/commission-regulation-eu-no-13212014',
            language='en'
        ),
        
        # FAA - USA
        RegulationSource(
            authority='FAA',
            region='North America',
            document_code='Order 8900.1',
            url='https://www.faa.gov/regulations_policies/orders_notices/index.cfm/go/document.information/documentID/1027770',
            language='en'
        ),
        RegulationSource(
            authority='FAA',
            region='North America',
            document_code='AC 65-30',
            url='https://www.faa.gov/regulations_policies/advisory_circulars/index.cfm/go/document.information/documentID/1034695',
            language='en'
        ),
        
        # UK CAA - Reino Unido
        RegulationSource(
            authority='UK CAA',
            region='United Kingdom',
            document_code='CAP 741',
            url='https://publicapps.caa.co.uk/modalapplication.aspx?catid=1&pagetype=65&appid=11&mode=detail&id=325',
            language='en'
        ),
        
        # DGAC México
        RegulationSource(
            authority='DGAC Mexico',
            region='Latin America',
            document_code='LAR 66',
            url='https://www.gob.mx/afac/documentos/reglamentos-mexicanos',
            language='es'
        ),
        
        # RAC Colombia
        RegulationSource(
            authority='RAC Colombia',
            region='Latin America',
            document_code='LPTA 66',
            url='https://www.aerocivil.gov.co/normatividad/RAC/RAC%20%20066%20-%20Licencias%20y%20Habilitaciones%20del%20Personal%20T%C3%A9cnico%20Aeron%C3%A1utico.pdf',
            language='es'
        ),
        
        # ICAO - Internacional
        RegulationSource(
            authority='ICAO',
            region='International',
            document_code='Doc 9859',
            url='https://www.icao.int/safety/SafetyManagement/Documents/Doc.9859.3rd%20Edition.alltext.en.pdf',
            language='en'
        ),
        RegulationSource(
            authority='ICAO',
            region='International',
            document_code='Doc 7192',
            url='https://store.icao.int/en/training-manual-doc-7192',
            language='en'
        ),
    ]
    
    def __init__(self, output_dir: Path = Path("./docs/knowledge_item/world_regs")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Headers para simular navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"✓ Output directory: {self.output_dir}")
    
    def download_pdf(self, source: RegulationSource) -> Optional[Path]:
        """
        Descarga un PDF de una fuente oficial
        
        Args:
            source: Fuente de regulación
        
        Returns:
            Ruta al archivo descargado o None si falló
        """
        print(f"\n📥 Descargando: {source.document_code} ({source.authority})")
        print(f"   URL: {source.url}")
        
        try:
            # Si ya es un PDF directo
            if source.url.endswith('.pdf'):
                response = requests.get(source.url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    # Generar nombre de archivo
                    filename = f"{source.authority.replace(' ', '_')}_{source.document_code.replace(' ', '_')}_{source.language}.pdf"
                    file_path = self.output_dir / filename
                    
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Calcular hash
                    file_hash = hashlib.sha256(response.content).hexdigest()
                    
                    print(f"   ✓ Descargado: {filename}")
                    print(f"   SHA-256: {file_hash[:16]}...")
                    print(f"   Tamaño: {len(response.content) / 1024:.1f} KB")
                    
                    return file_path
                else:
                    print(f"   ✗ Error HTTP {response.status_code}")
                    return None
            
            else:
                # Es una página web, intentar extraer link de descarga
                response = requests.get(source.url, headers=self.headers, timeout=30)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Buscar enlaces a PDF
                    pdf_links = soup.find_all('a', href=lambda href: href and '.pdf' in href.lower())
                    
                    if pdf_links:
                        # Tomar el primer PDF encontrado
                        pdf_url = pdf_links[0]['href']
                        
                        # Hacer URL absoluta
                        if not pdf_url.startswith('http'):
                            pdf_url = urljoin(source.url, pdf_url)
                        
                        print(f"   📄 Encontrado PDF: {pdf_url}")
                        
                        # Descargar
                        pdf_response = requests.get(pdf_url, headers=self.headers, timeout=30)
                        
                        if pdf_response.status_code == 200:
                            filename = f"{source.authority.replace(' ', '_')}_{source.document_code.replace(' ', '_')}_{source.language}.pdf"
                            file_path = self.output_dir / filename
                            
                            with open(file_path, 'wb') as f:
                                f.write(pdf_response.content)
                            
                            file_hash = hashlib.sha256(pdf_response.content).hexdigest()
                            
                            print(f"   ✓ Descargado: {filename}")
                            print(f"   SHA-256: {file_hash[:16]}...")
                            print(f"   Tamaño: {len(pdf_response.content) / 1024:.1f} KB")
                            
                            return file_path
                    else:
                        print(f"   ⚠️  No se encontraron PDFs en la página")
                        print(f"   Guardando metadata para descarga manual...")
                        
                        # Guardar metadata
                        self._save_manual_download_metadata(source)
                        
                        return None
                else:
                    print(f"   ✗ Error HTTP {response.status_code}")
                    return None
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return None
    
    def _save_manual_download_metadata(self, source: RegulationSource):
        """Guarda metadata para descarga manual"""
        metadata_file = self.output_dir / "MANUAL_DOWNLOAD_REQUIRED.md"
        
        with open(metadata_file, 'a', encoding='utf-8') as f:
            f.write(f"\n## {source.document_code} ({source.authority})\n\n")
            f.write(f"- **Región:** {source.region}\n")
            f.write(f"- **URL:** {source.url}\n")
            f.write(f"- **Idioma:** {source.language}\n")
            f.write(f"- **Fecha:** {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write(f"- **Instrucciones:** Descargar manualmente desde la URL y colocar en este directorio\n")
            f.write(f"\n---\n")
    
    def download_all_sources(self, delay_seconds: int = 2) -> Dict[str, int]:
        """
        Descarga todas las fuentes del catálogo
        
        Args:
            delay_seconds: Delay entre requests (respetar servidores)
        
        Returns:
            Estadísticas de descarga
        """
        stats = {
            'total': len(self.OFFICIAL_SOURCES),
            'downloaded': 0,
            'failed': 0,
            'manual_required': 0
        }
        
        print("\n" + "="*70)
        print("SCRAPER GLOBAL DE NORMATIVAS OJT")
        print("="*70)
        print(f"Total de fuentes: {stats['total']}")
        print(f"Output directory: {self.output_dir}")
        
        for idx, source in enumerate(self.OFFICIAL_SOURCES, 1):
            print(f"\n[{idx}/{stats['total']}]")
            
            result = self.download_pdf(source)
            
            if result:
                stats['downloaded'] += 1
            else:
                stats['failed'] += 1
                
                # Verificar si requiere descarga manual
                if (self.output_dir / "MANUAL_DOWNLOAD_REQUIRED.md").exists():
                    stats['manual_required'] += 1
            
            # Delay para no saturar servidores
            if idx < stats['total']:
                time.sleep(delay_seconds)
        
        print("\n" + "="*70)
        print("RESUMEN DE DESCARGA")
        print("="*70)
        print(f"✓ Descargados exitosamente: {stats['downloaded']}")
        print(f"✗ Fallidos: {stats['failed']}")
        print(f"⚠️  Requieren descarga manual: {stats['manual_required']}")
        
        return stats

# Ejemplo de uso
if __name__ == "__main__":
    scraper = GlobalRegulationsScraper()
    
    stats = scraper.download_all_sources(delay_seconds=2)
    
    print("\n" + "="*70)
    print("PRÓXIMOS PASOS")
    print("="*70)
    print("1. Revisar archivos descargados en:")
    print(f"   {scraper.output_dir}")
    print("\n2. Si hay documentos en MANUAL_DOWNLOAD_REQUIRED.md:")
    print("   - Descargar manualmente desde las URLs indicadas")
    print("   - Colocar PDFs en el directorio de output")
    print("\n3. Ejecutar conversión PDF→Markdown:")
    print("   python backend/scripts/pdf_to_markdown.py")
    print("\n4. Indexar en ChromaDB:")
    print("   python backend/scripts/rag_indexing.py")
