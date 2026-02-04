# OnTrackIA OJT V2.0 - Documentación PDFOverlayService

## 📋 Descripción General

El **PDFOverlayService** es el sistema forense de estampado de datos sobre formatos oficiales de aviación. Permite "calcar" datos de la base de datos PostgreSQL directamente sobre PDFs blancos de autoridades (EASA, RAC, CAA) con sellado SHA-256 y trazabilidad GPS.

---

## 🎯 ¿Qué Problema Resuelve?

**Problema:** Los formatos oficiales (AAC F1, CAP 741, LPTA 66) requieren ser llenados manualmente, lo que genera:

- ❌ Errores de transcripción
- ❌ Letra ilegible
- ❌ Falta de trazabilidad
- ❌ Manipulación post-firma

**Solución:** PDFOverlayService estampa datos digitalmente sobre el formato oficial con:

- ✅ Precisión pixel-perfect
- ✅ Hanging Seal SHA-256 (auditable)
- ✅ Geolocalización GPS de la estación
- ✅ Inmutabilidad forense

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│  1. CARGA DE FORMATO BASE (PDF oficial EAS A/RAC)       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  2. CARGA DE MAPA DE COORDENADAS (.json)                │
│     Define dónde escribir cada dato (X, Y en mm)        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  3. DATOS DE POSTGRES (Técnico, Tareas, GPS, Fechas)   │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  4. INYECCIÓN FORENSE (Python + ReportLab)              │
│     - Overlay de texto en coordenadas exactas           │
│     - Hanging Seal SHA-256 en margen                    │
│     - Metadata con GPS y timestamp                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  5. PDF SELLADO LISTO PARA AUTORIDAD                    │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura de Archivos

```
backend/
├── services/
│   └── pdf_overlay.py          # Servicio principal
├── templates/
│   ├── aac_f1_blank.pdf        # PDF base AAC F1
│   ├── aac_f1_coordinates.json # Mapeo de coordenadas
│   ├── cap_741_blank.pdf       # PDF base CAP 741
│   ├── cap_741_coordinates.json# Mapeo CAP 741
│   ├── lpta66_blank.pdf        # PDF base RAC LPTA 66
│   └── lpta66_coordinates.json # Mapeo LPTA 66
└── output/
    └── (PDFs generados)
```

---

## 🗂️ Formato del Mapa JSON

Cada formato oficial tiene un archivo `.json` que define **exactamente** dónde escribir cada dato.

### Ejemplo: `aac_f1_coordinates.json`

```json
{
  "format_id": "aac_f1",
  "format_name": "AAC Form F1 - Aircraft Maintenance Experience Certificate",
  "authority": "Salvadoran Aviation Authority (AAC)",
  "version": "2024.1",
  "page_size": {
    "width_mm": 210,
    "height_mm": 297,
    "format": "A4"
  },
  "fields": [
    {
      "field_name": "technician_name",
      "label": "Nombre del Técnico",
      "x": 45,           // Coordenada X en mm (desde esquina inferior izquierda)
      "y": 240,          // Coordenada Y en mm
      "font_size": 11,
      "font_name": "Helvetica-Bold",
      "max_width": 120,
      "alignment": "left"
    },
    {
      "field_name": "license_number",
      "x": 45,
      "y": 225,
      "font_size": 10,
      "font_name": "Helvetica"
    }
    // ... más campos
  ],
  "seal_position": {
    "position": "bottom-right",
    "x": 150,
    "y": 10
  }
}
```

### Campos del Mapa JSON

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `field_name` | String | Nombre del campo en la BD |
| `x` | Float | Coordenada X en mm (desde esquina inferior izq.) |
| `y` | Float | Coordenada Y en mm |
| `font_size` | Integer | Tamaño de fuente (puntos) |
| `font_name` | String | Nombre de fuente (Helvetica, Courier, etc.) |
| `max_width` | Float (opcional) | Ancho máximo en mm |
| `alignment` | String | Alineación: left, center, right |

---

## 🔧 Cómo Obtener las Coordenadas

### Método 1: Adobe Acrobat

1. Abrir PDF en Adobe Acrobat Pro
2. Herramientas → Editar PDF → Agregar texto
3. Colocar cursor en la posición deseada
4. Ver coordenadas en la barra inferior (en puntos)
5. Convertir a mm: `mm = puntos / 2.834645669`

### Método 2: PDF-XChange Editor

1. Abrir PDF en PDF-XChange Editor
2. Herramientas → Medición → Regla
3. Medir desde esquina inferior izquierda
4. Las coordenadas se muestran en mm directamente

### Método 3: PyPDF2 + Script Python

```python
from PyPDF2 import PdfReader

pdf = PdfReader("formato.pdf")
page = pdf.pages[0]
width = float(page.mediabox.width)  / 2.834645669  # Convertir a mm
height = float(page.mediabox.height) / 2.834645669

print(f"Tamaño de página: {width}mm x {height}mm")
```

---

## 🚀 Uso del Servicio

### 1. Crear Template

```python
from pdf_overlay import PDFOverlayService, FormatTemplate

service = PDFOverlayService()

template = FormatTemplate(
    format_id="aac_f1",
    format_name="AAC Form F1",
    authority="AAC",
    base_pdf_path="./templates/aac_f1_blank.pdf",
    coordinate_map_path="./templates/aac_f1_coordinates.json",
    version="2024.1"
)
```

### 2. Preparar Datos

```python
data = {
    "technician_name": "Juan Pérez González",
    "license_number": "AMT-2024-001",
    "aircraft_type": "Airbus A320",
    "total_hours": "1500",
    "supervisor_name": "Carlos Rodríguez"
}

gps_coords = {
    "latitude": 13.692940,
    "longitude": -89.218191,
    "accuracy": 12.5
}

workstation_info = {
    "hostname": "OJT-WS-001",
    "user": "supervisor_carlos",
    "station_id": "MSLP-HANGAR-A"
}
```

### 3. Generar PDF Sellado

```python
output_path = service.generate_stamped_pdf(
    template=template,
    data=data,
    gps_coords=gps_coords,
    workstation_info=workstation_info,
    output_filename="aac_f1_juan_perez_2026.pdf"
)

print(f"✅ PDF generado: {output_path}")
```

**Salida:**

```
✅ PDF generado: ./output/aac_f1_juan_perez_2026.pdf
🔐 Hanging Seal: a7f3c9e42d1b8f6a...
📍 GPS: 13.692940, -89.218191
```

---

## 🔐 Hanging Seal (Sello Forense)

El **Hanging Seal** es un hash SHA-256 que:

- Se calcula a partir de TODOS los datos del documento
- Incluye GPS, timestamp, tenant_id, user_id
- Se imprime en el margen del PDF en color morado (#7c3aed)
- Permite verificar la integridad del documento

### Ejemplo de Hanging Seal

```
┌──────────────────────────────────────────────────┐
│ FORENSIC SEAL:                                   │
│ a7f3c9e42d1b8f6a91c2d4e5f6a7b8c9d0e1f2a3b4c5 │
│ d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6 │
└──────────────────────────────────────────────────┘
```

### Cómo Verificar el Sello

```python
from forensic_hash import ForensicHashService

# Recalcular sello con datos originales
recalculated_seal = ForensicHashService.calculate_forensic_seal(
    file_content=file_bytes,
    gps_coords=gps,
    tenant_id=1,
    uploaded_by=42,
    metadata={"task_code": "ATA-71-001"}
)

# Comparar con el sello original
is_valid = (original_seal == recalculated_seal)

if is_valid:
    print("✅ Documento VÁLIDO - No ha sido alterado")
else:
    print("❌ Documento INVÁLIDO - Ha sido manipulado")
```

---

## 📊 Formatos Soportados

| Formato | Código | Autoridad | Uso |
|---------|--------|-----------|-----|
| **AAC F1** | `aac_f1` | AAC (El Salvador) | Certificación de experiencia |
| **AAC F2** | `aac_f2` | AAC (El Salvador) | Registro de tareas específicas |
| **CAP 741** | `cap_741` | UK CAA | ATA chapter task log |
| **LPTA 66** | `lpta66` | RAC (Chile) | Practical training appendix 1 |

---

## 🎨 Integración con Dashboard

### Frontend: Botón de Generación

```jsx
import { FileText } from 'lucide-react';

const GenerateCertificateButton = ({ technicianId }) => {
  const handleGenerate = async () => {
    const response = await fetch('/api/ojt/generate-certificate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        technician_id: technicianId,
        format_id: 'aac_f1'
      })
    });

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'certificate_aac_f1.pdf';
    a.click();
  };

  return (
    <button className="btn" onClick={handleGenerate}>
      <FileText size={20} />
      Generar Certificado AAC F1
    </button>
  );
};
```

### Backend: API Endpoint

```python
from fastapi import APIRouter
from pdf_overlay import PDFOverlayService

router = APIRouter()

@router.post("/generate-certificate")
async def generate_certificate(
    technician_id: int,
    format_id: str,
    db: Session = Depends(get_db)
):
    # Obtener datos del técnico
    technician = db.query(OJTPerson).filter_by(id=technician_id).first()
    
    # Obtener GPS de la estación
    gps_coords = get_workstation_gps()
    
    # Generar PDF
    service = PDFOverlayService()
    pdf_path = service.generate_stamped_pdf(...)
    
    # Retornar PDF
    return FileResponse(pdf_path, media_type='application/pdf')
```

---

## ✅ Checklist de Implementación

- [ ] Instalar dependencias: `pip install reportlab PyPDF2`
- [ ] Crear directorio `templates/` con PDFs base
- [ ] Crear archivos JSON de mapeo de coordenadas
- [ ] Medir coordenadas exactas con Adobe Acrobat
- [ ] Probar generación de PDF con datos de prueba
- [ ] Verificar que el Hanging Seal se imprime correctamente
- [ ] Integrar con API endpoint
- [ ] Crear botón en frontend
- [ ] Probar descarga de PDF desde navegador
- [ ] Auditar con inspector de aviación

---

## 🔧 Troubleshooting

### Problema: Texto desalineado

**Causa:** Coordenadas incorrectas  
**Solución:** Re-medir con herramienta PDF, verificar que sean mm y no puntos

### Problema: Fuente no disponible

**Causa:** Fuente especificada no existe  
**Solución:** Usar fuentes estándar (Helvetica, Courier, Times-Roman)

### Problema: Hanging Seal no visible

**Causa:** Posición fuera del área imprimible  
**Solución:** Ajustar `seal_position` en JSON a coordenadas válidas

---

## 📚 Referencias

- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [AAC Form F1 Template](https://aac.gob.sv/forms/f1.pdf)
- [UK CAA CAP 741](https://publicapps.caa.co.uk/docs/33/CAP741.pdf)
- [RAC LPTA 66](https://www.dgac.gob.cl/normativa/lpta66.pdf)

---

**Autor:** OnTrackia Dev Team  
**Fecha:** 2026-02-04  
**Versión:** 2.0.0
