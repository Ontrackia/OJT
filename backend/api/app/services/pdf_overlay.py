#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - PDF Overlay Service
=========================================
Servicio para estampar datos sobre formatos oficiales de aviación
con sellado forense SHA-256 (Hanging Seal).

Soporta formatos:
- AAC F1/F2 (Experience certification)
- UK CAA CAP 741 (ATA chapter registration)
- RAC LPTA 66 Appendix 1 (Practical training log)

El sistema utiliza archivos JSON de mapeo de coordenadas para saber
exactamente dónde escribir cada dato en el PDF oficial.

Características:
- Overlay de datos sobre PDF base
- Hanging Seal SHA-256 en margen del documento
- Geolocalización GPS de la estación de trabajo
- Timestamp forense
- Firma digital del supervisor

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: Protocolo Búnker + Trazabilidad Ultimate
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader, PdfWriter
import io

@dataclass
class CoordinateMapping:
    """Mapeo de coordenadas para un campo en el PDF"""
    field_name: str
    x: float  # Coordenada X en mm desde la esquina inferior izquierda
    y: float  # Coordenada Y en mm desde la esquina inferior izquierda
    font_size: int = 10
    font_name: str = "Helvetica"
    max_width: Optional[float] = None  # Ancho máximo en mm
    alignment: str = "left"  # left, center, right

@dataclass
class FormatTemplate:
    """Template de formato oficial"""
    format_id: str
    format_name: str
    authority: str  # EASA, RAC, CAA
    base_pdf_path: str
    coordinate_map_path: str
    version: str

class PDFOverlayService:
    """
    Servicio de overlay PDF con sellado forense
    """
    
    def __init__(self):
        self.templates_dir = Path("./templates")
        self.output_dir = Path("./output")
        
        # Crear directorios si no existen
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
    
    def load_coordinate_map(self, map_path: str) -> List[CoordinateMapping]:
        """
        Carga el archivo JSON de mapeo de coordenadas
        
        Args:
            map_path: Ruta al archivo JSON
        
        Returns:
            Lista de mapeos de coordenadas
        """
        with open(map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        mappings = []
        for field in data.get("fields", []):
            mapping = CoordinateMapping(
                field_name=field["field_name"],
                x=field["x"],
                y=field["y"],
                font_size=field.get("font_size", 10),
                font_name=field.get("font_name", "Helvetica"),
                max_width=field.get("max_width"),
                alignment=field.get("alignment", "left")
            )
            mappings.append(mapping)
        
        return mappings
    
    def calculate_hanging_seal(
        self,
        data: Dict[str, Any],
        gps_coords: Dict[str, float],
        workstation_info: Dict[str, str]
    ) -> str:
        """
        Calcula el Hanging Seal (hash SHA-256) del documento
        
        Args:
            data: Datos del formulario
            gps_coords: Coordenadas GPS {latitude, longitude, accuracy}
            workstation_info: Info de la estación {hostname, user, station_id}
        
        Returns:
            Hash SHA-256 en hexadecimal
        """
        # Construir payload forense
        payload = {
            "data": data,
            "gps": gps_coords,
            "workstation": workstation_info,
            "timestamp_utc": datetime.utcnow().isoformat(),
            "seal_version": "2.0"
        }
        
        # Serializar a JSON determinístico
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode('utf-8')
        
        # Calcular hash
        return hashlib.sha256(payload_json).hexdigest()
    
    def create_overlay(
        self,
        mappings: List[CoordinateMapping],
        data: Dict[str, Any],
        page_size: tuple = A4
    ) -> bytes:
        """
        Crea una capa de overlay con los datos
        
        Args:
            mappings: Lista de mapeos de coordenadas
            data: Diccionario con los datos a escribir
            page_size: Tamaño de la página (default: A4)
        
        Returns:
            PDF overlay en bytes
        """
        # Crear buffer en memoria
        packet = io.BytesIO()
        
        # Crear canvas
        c = canvas.Canvas(packet, pagesize=page_size)
        c.setFillColor(black)
        
        # Escribir cada campo
        for mapping in mappings:
            value = data.get(mapping.field_name, "")
            
            if not value:
                continue
            
            # Convertir mm a puntos (1mm = 2.834645669 points)
            x_points = mapping.x * mm
            y_points = mapping.y * mm
            
            # Configurar fuente
            c.setFont(mapping.font_name, mapping.font_size)
            
            # Alinear texto
            if mapping.alignment == "center" and mapping.max_width:
                width = c.stringWidth(str(value), mapping.font_name, mapping.font_size)
                x_points = x_points + (mapping.max_width * mm - width) / 2
            elif mapping.alignment == "right" and mapping.max_width:
                width = c.stringWidth(str(value), mapping.font_name, mapping.font_size)
                x_points = x_points + mapping.max_width * mm - width
            
            # Escribir texto
            c.drawString(x_points, y_points, str(value))
        
        # Guardar canvas
        c.save()
        
        # Mover al inicio del buffer
        packet.seek(0)
        
        return packet.getvalue()
    
    def add_hanging_seal(
        self,
        pdf_canvas: canvas.Canvas,
        seal_hash: str,
        position: str = "bottom-right"
    ):
        """
        Agrega el Hanging Seal al margen del PDF
        
        Args:
            pdf_canvas: Canvas del PDF
            seal_hash: Hash SHA-256 a imprimir
            position: Posición del sello (bottom-right, bottom-left, etc.)
        """
        # Configuración del sello
        font_size = 6
        font_name = "Courier"
        
        # Posición según parámetro
        if position == "bottom-right":
            x = A4[0] - 150
            y = 10
        elif position == "bottom-left":
            x = 10
            y = 10
        else:
            x = 10
            y = 10
        
        # Color morado oscuro para el sello
        seal_color = HexColor("#7c3aed")
        
        # Dibujar rectángulo de fondo
        pdf_canvas.setFillColor(HexColor("#0a051a"))
        pdf_canvas.setStrokeColor(seal_color)
        pdf_canvas.setLineWidth(0.5)
        pdf_canvas.rect(x - 2, y - 2, 144, 12, fill=1, stroke=1)
        
        # Escribir sello
        pdf_canvas.setFillColor(seal_color)
        pdf_canvas.setFont(font_name, font_size)
        
        # Escribir "FORENSIC SEAL:" label
        pdf_canvas.drawString(x, y + 4, "FORENSIC SEAL:")
        
        # Escribir hash (primeros 32 caracteres)
        pdf_canvas.drawString(x + 48, y + 4, seal_hash[:32])
        pdf_canvas.drawString(x + 48, y - 2, seal_hash[32:64])
    
    def generate_stamped_pdf(
        self,
        template: FormatTemplate,
        data: Dict[str, Any],
        gps_coords: Dict[str, float],
        workstation_info: Dict[str, str],
        output_filename: str
    ) -> str:
        """
        Genera PDF estampado con datos y sello forense
        
        Args:
            template: Template del formato oficial
            data: Datos a estampar
            gps_coords: Coordenadas GPS
            workstation_info: Info de la estación
            output_filename: Nombre del archivo de salida
        
        Returns:
            Ruta del archivo generado
        """
        # Cargar mapeo de coordenadas
        mappings = self.load_coordinate_map(template.coordinate_map_path)
        
        # Calcular Hanging Seal
        hanging_seal = self.calculate_hanging_seal(data, gps_coords, workstation_info)
        
        # Crear overlay
        overlay_bytes = self.create_overlay(mappings, data)
        overlay_pdf = PdfReader(io.BytesIO(overlay_bytes))
        
        # Cargar PDF base
        base_pdf = PdfReader(template.base_pdf_path)
        
        # Crear PDF de salida
        output_pdf = PdfWriter()
        
        # Fusionar overlay con cada página
        for page_num in range(len(base_pdf.pages)):
            page = base_pdf.pages[page_num]
            
            # Aplicar overlay si existe
            if page_num < len(overlay_pdf.pages):
                page.merge_page(overlay_pdf.pages[page_num])
            
            output_pdf.add_page(page)
        
        # Crear PDF final con Hanging Seal
        packet = io.BytesIO()
        final_canvas = canvas.Canvas(packet, pagesize=A4)
        
        # Agregar Hanging Seal en la primera página
        self.add_hanging_seal(final_canvas, hanging_seal)
        
        # Agregar metadata
        final_canvas.setAuthor("OnTrackIA OJT V2.0")
        final_canvas.setTitle(f"{template.format_name} - {data.get('technician_name', 'Unknown')}")
        final_canvas.setSubject(f"Forensic Sealed Document - {hanging_seal[:16]}")
        
        final_canvas.save()
        packet.seek(0)
        
        # Fusionar sello con PDF
        seal_pdf = PdfReader(packet)
        first_page = output_pdf.pages[0]
        first_page.merge_page(seal_pdf.pages[0])
        
        # Guardar archivo final
        output_path = self.output_dir / output_filename
        with open(output_path, 'wb') as f:
            output_pdf.write(f)
        
        print(f"✅ PDF generado: {output_path}")
        print(f"🔐 Hanging Seal: {hanging_seal}")
        print(f"📍 GPS: {gps_coords['latitude']}, {gps_coords['longitude']}")
        
        return str(output_path)

# Ejemplo de uso
if __name__ == "__main__":
    service = PDFOverlayService()
    
    # Template de ejemplo (AAC F1)
    template = FormatTemplate(
        format_id="aac_f1",
        format_name="AAC Form F1 - Experience Certificate",
        authority="AAC (Salvadoran Aviation Authority)",
        base_pdf_path="./templates/aac_f1_blank.pdf",
        coordinate_map_path="./templates/aac_f1_coordinates.json",
        version="2024.1"
    )
    
    # Datos de ejemplo
    data = {
        "technician_name": "Juan Pérez González",
        "license_number": "AMT-2024-001",
        "aircraft_type": "Airbus A320",
        "total_hours": "1500",
        "date": "2026-02-04",
        "supervisor_name": "Carlos Rodríguez",
        "supervisor_license": "AMT-INSP-2020-045"
    }
    
    # GPS de ejemplo (San Salvador, El Salvador)
    gps_coords = {
        "latitude": 13.692940,
        "longitude": -89.218191,
        "accuracy": 12.5
    }
    
    # Info de estación
    workstation_info = {
        "hostname": "OJT-WS-001",
        "user": "supervisor_carlos",
        "station_id": "MSLP-HANGAR-A"
    }
    
    # Generar PDF
    output = service.generate_stamped_pdf(
        template=template,
        data=data,
        gps_coords=gps_coords,
        workstation_info=workstation_info,
        output_filename="aac_f1_juan_perez_2026.pdf"
    )
    
    print(f"\n📄 Documento generado: {output}")
