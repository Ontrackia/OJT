#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - PDF to Markdown Converter
===============================================
Conversor de normativas PDF a Markdown para sistema RAG

Features:
- Extracción de texto manteniendo jerarquía
- Limpieza de headers/footers
- Detección de títulos y secciones
- Soporte bilingüe ES/EN

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: EASA Part-66/145, RAC LPTA 66, CAA CAP 741
"""

import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import hashlib
from datetime import datetime

@dataclass
class DocumentMetadata:
    """Metadatos del documento normativo"""
    source: str
    authority: str  # EASA, RAC, CAA, FAA
    document_code: str  # Part-66, LPTA 66, CAP 741
    version: str
    publication_date: Optional[str]
    criticality_level: str  # high, medium, low
    language: str  # es, en

class PDFToMarkdownConverter:
    """
    Conversor de PDF normativo a Markdown estructurado
    """
    
    # Patrones de headers/footers a eliminar
    NOISE_PATTERNS = [
        r'Page \d+ of \d+',
        r'Página \d+ de \d+',
        r'EASA Form \d+',
        r'©.*\d{4}',
        r'Printed on.*',
        r'Impreso en.*',
        r'^-+\s*$',  # Líneas de guiones
        r'^\s*\d+\s*$',  # Números de página solos
    ]
    
    # Patrones de títulos (mayúsculas, negrita, etc.)
    TITLE_PATTERNS = [
        (r'^([A-Z\s]{10,})$', 1),  # TÍTULO TODO MAYÚSCULAS (h1)
        (r'^(\d+\.\s+[A-Z][^.]+)$', 2),  # 1. Título Capitalizado (h2)
        (r'^(\d+\.\d+\s+[A-Z][^.]+)$', 3),  # 1.1 Subtítulo (h3)
        (r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+):$', 2),  # Título Con Capitales: (h2)
    ]
    
    def __init__(self):
        self.current_metadata: Optional[DocumentMetadata] = None
    
    def clean_text(self, text: str) -> str:
        """Limpia headers, footers y ruido del texto"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Eliminar líneas que coincidan con patrones de ruido
            is_noise = any(re.search(pattern, line.strip()) for pattern in self.NOISE_PATTERNS)
            
            if not is_noise and line.strip():
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def detect_title_level(self, line: str) -> Optional[int]:
        """Detecta si una línea es un título y retorna su nivel (1-3)"""
        for pattern, level in self.TITLE_PATTERNS:
            if re.match(pattern, line.strip()):
                return level
        return None
    
    def format_as_markdown(self, line: str, title_level: Optional[int] = None) -> str:
        """Formatea una línea como Markdown"""
        if title_level:
            return f"{'#' * title_level} {line.strip()}"
        return line
    
    def extract_metadata_from_pdf(self, pdf_path: Path) -> DocumentMetadata:
        """Extrae metadatos del PDF"""
        doc = fitz.open(pdf_path)
        
        # Leer metadata del PDF
        pdf_metadata = doc.metadata
        
        # Intentar detectar autoridad del nombre del archivo
        filename = pdf_path.stem.lower()
        
        if 'easa' in filename or 'part' in filename:
            authority = 'EASA'
            document_code = 'Part-66' if 'part-66' in filename or 'part_66' in filename else 'Part-145'
        elif 'rac' in filename or 'lpta' in filename:
            authority = 'RAC'
            document_code = 'LPTA 66'
        elif 'caa' in filename or 'cap' in filename:
            authority = 'UK CAA'
            document_code = 'CAP 741'
        elif 'faa' in filename:
            authority = 'FAA'
            document_code = 'Order 8900.1'
        else:
            authority = 'Unknown'
            document_code = 'Unknown'
        
        # Detectar idioma del primer párrafo
        first_page_text = doc[0].get_text()
        language = 'en' if len(re.findall(r'\b[a-zA-Z]+\b', first_page_text)) > 50 else 'es'
        
        doc.close()
        
        return DocumentMetadata(
            source=pdf_path.name,
            authority=authority,
            document_code=document_code,
            version='1.0',  # Ajustar según necesidad
            publication_date=datetime.now().strftime('%Y-%m-%d'),
            criticality_level='high',
            language=language
        )
    
    def convert_pdf_to_markdown(self, pdf_path: Path, output_dir: Path) -> Path:
        """
        Convierte un PDF normativo a Markdown estructurado
        
        Args:
            pdf_path: Ruta al PDF
            output_dir: Directorio de salida
        
        Returns:
            Ruta al archivo Markdown generado
        """
        print(f"\nProcesando: {pdf_path.name}")
        
        # Extraer metadata
        self.current_metadata = self.extract_metadata_from_pdf(pdf_path)
        print(f"  Autoridad: {self.current_metadata.authority}")
        print(f"  Código: {self.current_metadata.document_code}")
        print(f"  Idioma: {self.current_metadata.language}")
        
        # Abrir PDF
        doc = fitz.open(pdf_path)
        
        # Contenido markdown
        markdown_lines = []
        
        # Header del documento
        markdown_lines.append(f"# {self.current_metadata.document_code}")
        markdown_lines.append(f"**Autoridad:** {self.current_metadata.authority}  ")
        markdown_lines.append(f"**Fuente:** {self.current_metadata.source}  ")
        markdown_lines.append(f"**Fecha:** {self.current_metadata.publication_date}  ")
        markdown_lines.append(f"**Nivel de Criticidad:** {self.current_metadata.criticality_level}  ")
        markdown_lines.append(f"**Idioma:** {self.current_metadata.language}  ")
        markdown_lines.append("\n---\n")
        
        # Procesar cada página
        for page_num, page in enumerate(doc, start=1):
            print(f"  Página {page_num}/{len(doc)}", end='\r')
            
            # Extraer texto
            text = page.get_text()
            
            # Limpiar
            cleaned_text = self.clean_text(text)
            
            # Procesar líneas
            for line in cleaned_text.split('\n'):
                if not line.strip():
                    continue
                
                # Detectar si es título
                title_level = self.detect_title_level(line)
                
                # Formatear
                formatted_line = self.format_as_markdown(line, title_level)
                markdown_lines.append(formatted_line)
        
        doc.close()
        print(f"\n  ✓ Procesamiento completado")
        
        # Generar nombre de salida
        output_filename = f"{pdf_path.stem}.md"
        output_path = output_dir / output_filename
        
        # Escribir archivo
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        print(f"  ✓ Guardado en: {output_path}")
        
        # Calcular hash del documento
        with open(output_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        print(f"  SHA-256: {file_hash[:16]}...")
        
        return output_path

# Ejemplo de uso
if __name__ == "__main__":
    converter = PDFToMarkdownConverter()
    
    # Directorio de PDFs
    pdf_dir = Path("./regulations/pdfs")
    output_dir = Path("./docs/knowledge_item")
    
    if pdf_dir.exists():
        for pdf_file in pdf_dir.glob("*.pdf"):
            try:
                converter.convert_pdf_to_markdown(pdf_file, output_dir)
            except Exception as e:
                print(f"  ✗ Error procesando {pdf_file.name}: {e}")
    else:
        print(f"Directorio {pdf_dir} no encontrado")
        print("Crea el directorio y coloca los PDFs de normativas ahí:")
        print("  - EASA Part-66.pdf")
        print("  - EASA Part-145.pdf")
        print("  - RAC LPTA 66.pdf")
        print("  - UK CAA CAP 741.pdf")
        print("  - FAA Order 8900.1.pdf")
