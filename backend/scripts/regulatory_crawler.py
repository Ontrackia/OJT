#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Global Regulatory Crawler
===============================================
"Cielos Abiertos" Vision - Worldwide Aviation Authority Crawler

Descarga y procesa regulaciones de mantenimiento (Part 145/M/66 equivalentes)
y SMS de autoridades aeronáuticas mundiales.

TERRITORIOS CUBIERTOS:
- Commonwealth & Asia: CASA, TCCA, UK CAA, QCAA, CAAC
- Latam & Caribe: ANAC Brasil, AFAC México, Costa Rica, Ecuador, Chile
- Europa no-EASA: FOCA Suiza, TM CAD Malta
- África: SACAA Sudáfrica, KCAA Kenia

@author OnTrackia Dev Team
@date 2026-02-04
"""

import os
import sys
import requests
from pathlib import Path
from typing import Dict, List
import json
from datetime import datetime
import hashlib
import time

# PDF processing
try:
    import pdfplumber
    import PyPDF2
except ImportError:
    print("⚠️  PDF libraries not installed. Run: pip install pdfplumber PyPDF2")
    sys.exit(1)

# Web scraping
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("⚠️  BeautifulSoup not installed. Run: pip install beautifulsoup4")
    sys.exit(1)


class GlobalRegulatoryCrawler:
    """
    Crawler universal para autoridades aeronáuticas mundiales
    """
    
    # Configuración de autoridades por territorio
    AUTHORITIES = {
        # Commonwealth & Asia
        'AUSTRALIA': {
            'name': 'CASA - Civil Aviation Safety Authority',
            'abbreviation': 'CASA',
            'urls': {
                'part145': 'https://www.casa.gov.au/regulations-and-policy/current-rules',
                'sms': 'https://www.casa.gov.au/safety-management/safety-management-systems'
            },
            'keywords': ['CASR Part 145', 'AMO', 'Safety Management']
        },
        'CANADA': {
            'name': 'TCCA - Transport Canada Civil Aviation',
            'abbreviation': 'TCCA',
            'urls': {
                'part145': 'https://tc.canada.ca/en/aviation/reference-centre/canadian-aviation-regulations-cars',
                'sms': 'https://tc.canada.ca/en/aviation/commercial-air-services/safety-management-systems'
            },
            'keywords': ['CAR 573', 'AMO', 'SMS']
        },
        'UK': {
            'name': 'UK CAA - Civil Aviation Authority',
            'abbreviation': 'UK CAA',
            'urls': {
                'part145': 'https://www.caa.co.uk/commercial-industry/aircraft/aircraft-maintenance/',
                'cap': 'https://publicapps.caa.co.uk/docs/33/CAP%20562%20Civil%20Aircraft%20Airworthiness.pdf'
            },
            'keywords': ['Part-145', 'CAP 562', 'CAME']
        },
        'QATAR': {
            'name': 'QCAA - Qatar Civil Aviation Authority',
            'abbreviation': 'QCAA',
            'urls': {
                'regulations': 'https://www.caa.gov.qa/En/Regulations/Pages/default.aspx'
            },
            'keywords': ['QCAR', 'Part M', 'Part 145']
        },
        'CHINA': {
            'name': 'CAAC - Civil Aviation Administration of China',
            'abbreviation': 'CAAC',
            'urls': {
                'regulations': 'http://www.caac.gov.cn/en/'
            },
            'keywords': ['CCAR-145', 'Maintenance Organization']
        },
        
        # Latin America & Caribbean
        'BRAZIL': {
            'name': 'ANAC - Agência Nacional de Aviação Civil',
            'abbreviation': 'ANAC',
            'urls': {
                'rbac145': 'https://www.anac.gov.br/assuntos/legislacao/legislacao-1/rbac-e-is/rbac/rbac-145',
                'sgso': 'https://www.anac.gov.br/assuntos/seguranca-operacional/sgso'
            },
            'keywords': ['RBAC 145', 'RBAC 66', 'SGSO', 'RBHA']
        },
        'MEXICO': {
            'name': 'AFAC - Agencia Federal de Aviación Civil',
            'abbreviation': 'AFAC',
            'urls': {
                'regulations': 'https://www.gob.mx/afac/documentos/reglamentos-y-normas'
            },
            'keywords': ['RAC 145', 'Talleres Aeronáuticos', 'SMS']
        },
        'COSTA_RICA': {
            'name': 'DGAC Costa Rica',
            'abbreviation': 'DGAC CR',
            'urls': {
                'regulations': 'https://www.dgac.go.cr/normativa/'
            },
            'keywords': ['LAR 145', 'LAR 66', 'Talleres']
        },
        'ECUADOR': {
            'name': 'DGAC Ecuador',
            'abbreviation': 'DGAC EC',
            'urls': {
                'regulations': 'https://www.aviacioncivil.gob.ec/normativa/'
            },
            'keywords': ['RDAC 145', 'RAC']
        },
        'CHILE': {
            'name': 'DGAC Chile',
            'abbreviation': 'DGAC CL',
            'urls': {
                'regulations': 'https://www.dgac.gob.cl/normativa-y-regulacion/'
            },
            'keywords': ['DAN 145', 'DGAC']
        },
        
        # Europe (Non-EASA)
        'SWITZERLAND': {
            'name': 'FOCA - Federal Office of Civil Aviation',
            'abbreviation': 'FOCA',
            'urls': {
                'regulations': 'https://www.bazl.admin.ch/bazl/en/home/specialists/regulations.html'
            },
            'keywords': ['Part-145', 'Part-M', 'Part-66']
        },
        'MALTA': {
            'name': 'TM CAD - Transport Malta Civil Aviation',
            'abbreviation': 'TM CAD',
            'urls': {
                'regulations': 'https://www.transport.gov.mt/aviation/legislation'
            },
            'keywords': ['Part-145', 'EASA compliance']
        },
        
        # Africa
        'SOUTH_AFRICA': {
            'name': 'SACAA - South African Civil Aviation Authority',
            'abbreviation': 'SACAA',
            'urls': {
                'regulations': 'http://www.caa.co.za/Pages/RPAS/Regulations.aspx',
                'part145': 'http://www.caa.co.za/the%20regulations%20and%20legislations/regulations/Technical%20Standards/Part%20145%20Aircraft%20Maintenance%20Organizations%2001%20April%202012.pdf'
            },
            'keywords': ['Part 145', 'AMO', 'SACAA']
        },
        'KENYA': {
            'name': 'KCAA - Kenya Civil Aviation Authority',
            'abbreviation': 'KCAA',
            'urls': {
                'regulations': 'https://www.kcaa.or.ke/regulations'
            },
            'keywords': ['Part-145', 'AMO Approval']
        }
    }
    
    def __init__(self, base_dir: str = "./knowledge_base/global"):
        """
        Initialize crawler
        
        Args:
            base_dir: Base directory for knowledge base
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OnTrackIA-RegulatoryCrawler/2.0 (Aviation Safety Research)'
        })
        
        print("=" * 70)
        print("ONTRACKIA OJT V2.0 - GLOBAL REGULATORY CRAWLER")
        print('"Cielos Abiertos" Vision')
        print("=" * 70)
        print(f"Base Directory: {self.base_dir}")
        print(f"Authorities: {len(self.AUTHORITIES)}")
        print()
    
    def _download_pdf(self, url: str, output_path: Path) -> bool:
        """Download PDF from URL"""
        try:
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"   ❌ Error downloading {url}: {e}")
            return False
    
    def _pdf_to_markdown(self, pdf_path: Path, md_path: Path, metadata: Dict) -> bool:
        """Convert PDF to Markdown"""
        try:
            # Try pdfplumber first (better for structured PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                text_content = []
                
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(f"## Page {i + 1}\n\n{page_text}\n\n")
                
                full_text = "\n".join(text_content)
            
            # Create markdown with metadata header
            md_content = f"""---
territory: {metadata['territory']}
authority: {metadata['authority']}
abbreviation: {metadata['abbreviation']}
document_type: {metadata.get('doc_type', 'regulation')}
source_url: {metadata.get('source_url', 'N/A')}
crawled_at: {datetime.now().isoformat()}
---

# {metadata.get('title', 'Regulatory Document')}

**Authority**: {metadata['authority']} ({metadata['abbreviation']})  
**Territory**: {metadata['territory']}  
**Source**: {metadata.get('source_url', 'N/A')}

---

{full_text}
"""
            
            # Write markdown
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error converting PDF to MD: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    text_content = []
                    
                    for i, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(f"## Page {i + 1}\n\n{page_text}\n\n")
                    
                    full_text = "\n".join(text_content)
                
                # Create markdown
                md_content = f"""---
territory: {metadata['territory']}
authority: {metadata['authority']}
abbreviation: {metadata['abbreviation']}
document_type: {metadata.get('doc_type', 'regulation')}
source_url: {metadata.get('source_url', 'N/A')}
crawled_at: {datetime.now().isoformat()}
fallback_parser: PyPDF2
---

# {metadata.get('title', 'Regulatory Document')}

{full_text}
"""
                
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                
                return True
                
            except Exception as e2:
                print(f"   ❌ Fallback parser also failed: {e2}")
                return False
    
    def crawl_authority(self, territory: str, skip_existing: bool = True) -> Dict:
        """
        Crawl single authority
        
        Args:
            territory: Territory code (e.g., 'BRAZIL', 'CANADA')
            skip_existing: Skip if already downloaded
        
        Returns:
            Statistics dictionary
        """
        if territory not in self.AUTHORITIES:
            print(f"❌ Unknown territory: {territory}")
            return {}
        
        authority_info = self.AUTHORITIES[territory]
        
        print(f"\n{'='*70}")
        print(f"🌍 {territory}: {authority_info['name']}")
        print(f"{'='*70}")
        
        # Create territory directory
        territory_dir = self.base_dir / territory
        territory_dir.mkdir(parents=True, exist_ok=True)
        
        stats = {
            'territory': territory,
            'downloaded': 0,
            'converted': 0,
            'failed': 0,
            'files': []
        }
        
        # Process each URL
        for doc_type, url in authority_info['urls'].items():
            print(f"\n📥 Downloading {doc_type} from {url}...")
            
            # Generate filename
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            pdf_filename = f"{authority_info['abbreviation']}_{doc_type}_{url_hash}.pdf"
            md_filename = f"{authority_info['abbreviation']}_{doc_type}_{url_hash}.md"
            
            pdf_path = territory_dir / pdf_filename
            md_path = territory_dir / md_filename
            
            # Skip if exists
            if skip_existing and md_path.exists():
                print(f"   ⏭️  Already exists: {md_filename}")
                stats['files'].append(str(md_path))
                continue
            
            # Download PDF
            if self._download_pdf(url, pdf_path):
                print(f"   ✅ Downloaded: {pdf_filename}")
                stats['downloaded'] += 1
                
                # Convert to Markdown
                metadata = {
                    'territory': territory,
                    'authority': authority_info['name'],
                    'abbreviation': authority_info['abbreviation'],
                    'doc_type': doc_type,
                    'source_url': url,
                    'title': f"{authority_info['abbreviation']} - {doc_type.upper()}"
                }
                
                if self._pdf_to_markdown(pdf_path, md_path, metadata):
                    print(f"   ✅ Converted to MD: {md_filename}")
                    stats['converted'] += 1
                    stats['files'].append(str(md_path))
                    
                    # Remove PDF to save space
                    pdf_path.unlink()
                else:
                    stats['failed'] += 1
            else:
                stats['failed'] += 1
            
            # Respectful crawling - delay between requests
            time.sleep(2)
        
        # Save index
        index_path = territory_dir / "index.json"
        with open(index_path, 'w') as f:
            json.dump({
                'territory': territory,
                'authority': authority_info,
                'stats': stats,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        return stats
    
    def crawl_all(self, territories: List[str] = None, skip_existing: bool = True) -> Dict:
        """
        Crawl all authorities or specific list
        
        Args:
            territories: List of territory codes (None = all)
            skip_existing: Skip existing files
        
        Returns:
            Aggregated statistics
        """
        if territories is None:
            territories = list(self.AUTHORITIES.keys())
        
        print(f"\n🌐 Crawling {len(territories)} territories...")
        print(f"   Territories: {', '.join(territories)}")
        print()
        
        all_stats = {}
        
        for territory in territories:
            try:
                stats = self.crawl_authority(territory, skip_existing)
                all_stats[territory] = stats
            except Exception as e:
                print(f"\n❌ Error crawling {territory}: {e}")
                all_stats[territory] = {'error': str(e)}
        
        # Print summary
        print("\n" + "=" * 70)
        print("CRAWLING SUMMARY")
        print("=" * 70)
        
        total_downloaded = sum(s.get('downloaded', 0) for s in all_stats.values())
        total_converted = sum(s.get('converted', 0) for s in all_stats.values())
        total_failed = sum(s.get('failed', 0) for s in all_stats.values())
        
        print(f"✅ Downloaded: {total_downloaded}")
        print(f"✅ Converted to MD: {total_converted}")
        print(f"❌ Failed: {total_failed}")
        print()
        
        return all_stats


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='OnTrackIA Global Regulatory Crawler')
    parser.add_argument('--territory', type=str, help='Specific territory to crawl (e.g., BRAZIL, CANADA)')
    parser.add_argument('--all', action='store_true', help='Crawl all territories')
    parser.add_argument('--list', action='store_true', help='List available territories')
    parser.add_argument('--output', type=str, default='./knowledge_base/global', help='Output directory')
    parser.add_argument('--force', action='store_true', help='Re-download existing files')
    
    args = parser.parse_args()
    
    crawler = GlobalRegulatoryCrawler(base_dir=args.output)
    
    if args.list:
        print("\nAvailable Territories:")
        for territory, info in crawler.AUTHORITIES.items():
            print(f"  {territory:20s} - {info['name']}")
        return
    
    if args.all:
        crawler.crawl_all(skip_existing=not args.force)
    elif args.territory:
        territory = args.territory.upper()
        crawler.crawl_authority(territory, skip_existing=not args.force)
    else:
        print("Usage: python regulatory_crawler.py --all  OR  --territory BRAZIL")
        print("       python regulatory_crawler.py --list  (to see available territories)")


if __name__ == "__main__":
    main()
