#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Forensic Hash Service
============================================
Servicio de generación de hash SHA-256 con trazabilidad forense que incluye:
- Contenido del archivo
- Coordenadas GPS (latitude, longitude)
- Precisión GPS (accuracy)
- Timestamp de captura

Si las coordenadas GPS son nulas o inválidas, el sellado forense falla
para garantizar trazabilidad Ultimate.

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: Protocolo Búnker + Geolocalización Forense
"""

import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class GPSCoordinates:
    """Coordenadas GPS con validación"""
    latitude: float
    longitude: float
    accuracy: float
    timestamp: datetime
    
    def validate(self) -> bool:
        """
        Valida que las coordenadas GPS sean correctas
        
        Returns:
            True si las coordenadas son válidas
        
        Raises:
            ValueError si las coordenadas son inválidas
        """
        # Validar rango de latitud (-90 a 90)
        if not -90 <= self.latitude <= 90:
            raise ValueError(f"Latitud inválida: {self.latitude}. Debe estar entre -90 y 90")
        
        # Validar rango de longitud (-180 a 180)
        if not -180 <= self.longitude <= 180:
            raise ValueError(f"Longitud inválida: {self.longitude}. Debe estar entre -180 y 180")
        
        # Validar accuracy (debe ser positivo)
        if self.accuracy < 0:
            raise ValueError(f"Precisión GPS inválida: {self.accuracy}. Debe ser >= 0")
        
        # Advertir si la precisión es muy baja (>100 metros)
        if self.accuracy > 100:
            import warnings
            warnings.warn(
                f"⚠️ Precisión GPS baja: {self.accuracy}m. Recomendado: <50m",
                UserWarning
            )
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return {
            "latitude": f"{self.latitude:.6f}",
            "longitude": f"{self.longitude:.6f}",
            "accuracy": f"{self.accuracy:.2f}",
            "timestamp": self.timestamp.isoformat()
        }

class ForensicHashService:
    """
    Servicio de hashing forense con geolocalización
    Implementación del Protocolo Búnker V2.0
    """
    
    @staticmethod
    def calculate_file_hash(file_path: str) -> str:
        """
        Calcula hash SHA-256 del archivo
        
        Args:
            file_path: Ruta del archivo
        
        Returns:
            Hash SHA-256 en hexadecimal
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Leer en bloques de 4KB para eficiencia
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def calculate_forensic_seal(
        file_content: bytes,
        gps_coords: GPSCoordinates,
        tenant_id: int,
        uploaded_by: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera sello forense SHA-256 que incluye:
        - Contenido del archivo
        - Coordenadas GPS (latitude, longitude, accuracy, timestamp)
        - Tenant ID
        - User ID
        - Metadata adicional
        
        Args:
            file_content: Contenido del archivo en bytes
            gps_coords: Coordenadas GPS validadas
            tenant_id: ID del tenant
            uploaded_by: ID del usuario que sube
            metadata: Metadata adicional opcional
        
        Returns:
            Hash SHA-256 forense en hexadecimal
        
        Raises:
            ValueError: Si las coordenadas GPS son inválidas o nulas
        """
        # Validar GPS obligatorio
        if gps_coords is None:
            raise ValueError(
                "❌ GPS OBLIGATORIO: Las coordenadas GPS son requeridas para el sellado forense. "
                "Habilite la geolocalización en su dispositivo."
            )
        
        # Validar coordenadas
        gps_coords.validate()
        
        # Construir payload forense
        forensic_payload = {
            "file_hash": hashlib.sha256(file_content).hexdigest(),
            "gps": gps_coords.to_dict(),
            "tenant_id": tenant_id,
            "uploaded_by": uploaded_by,
            "seal_version": "2.0",
            "seal_timestamp": datetime.utcnow().isoformat()
        }
        
        # Agregar metadata si existe
        if metadata:
            forensic_payload["metadata"] = metadata
        
        # Serializar payload a JSON determinístico (ordenado)
        payload_json = json.dumps(
            forensic_payload,
            sort_keys=True,
            separators=(',', ':')
        ).encode('utf-8')
        
        # Calcular hash final
        seal_hash = hashlib.sha256(payload_json).hexdigest()
        
        return seal_hash
    
    @staticmethod
    def verify_forensic_seal(
        original_seal: str,
        file_content: bytes,
        gps_coords: GPSCoordinates,
        tenant_id: int,
        uploaded_by: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Verifica la integridad del sello forense
        
        Args:
            original_seal: Hash original almacenado
            file_content: Contenido del archivo
            gps_coords: Coordenadas GPS
            tenant_id: ID del tenant
            uploaded_by: ID del usuario
            metadata: Metadata adicional
        
        Returns:
            True si el sello es válido
        """
        # Recalcular sello
        recalculated_seal = ForensicHashService.calculate_forensic_seal(
            file_content=file_content,
            gps_coords=gps_coords,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            metadata=metadata
        )
        
        # Comparar
        return original_seal == recalculated_seal
    
    @staticmethod
    def format_gps_for_display(latitude: float, longitude: float) -> str:
        """
        Formatea coordenadas GPS para visualización
        
        Args:
            latitude: Latitud
            longitude: Longitud
        
        Returns:
            String formateado tipo "40.416775°N, -3.703790°W"
        """
        # Determinar hemisferios
        lat_dir = "N" if latitude >= 0 else "S"
        lon_dir = "E" if longitude >= 0 else "W"
        
        # Valores absolutos
        lat_abs = abs(latitude)
        lon_abs = abs(longitude)
        
        return f"{lat_abs:.6f}°{lat_dir}, {lon_abs:.6f}°{lon_dir}"
    
    @staticmethod
    def get_google_maps_url(latitude: float, longitude: float) -> str:
        """
        Genera URL de Google Maps para las coordenadas
        
        Args:
            latitude: Latitud
            longitude: Longitud
        
        Returns:
            URL de Google Maps
        """
        return f"https://www.google.com/maps?q={latitude},{longitude}"

# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo: Crear sello forense
    print("🔐 OnTrackIA OJT V2.0 - Forensic Hash Service")
    print("=" * 60)
    
    # Coordenadas de ejemplo (Madrid, España)
    gps = GPSCoordinates(
        latitude=40.416775,
        longitude=-3.703790,
        accuracy=15.5,
        timestamp=datetime.utcnow()
    )
    
    # Contenido de archivo de ejemplo
    file_content = b"Este es un ejemplo de evidencia OJT"
    
    # Calcular sello forense
    seal = ForensicHashService.calculate_forensic_seal(
        file_content=file_content,
        gps_coords=gps,
        tenant_id=1,
        uploaded_by=42,
        metadata={"task_code": "ATA-71-001"}
    )
    
    print(f"✅ Sello Forense: {seal}")
    print(f"📍 GPS: {ForensicHashService.format_gps_for_display(gps.latitude, gps.longitude)}")
    print(f"🗺️  Maps: {ForensicHashService.get_google_maps_url(gps.latitude, gps.longitude)}")
    print(f"🎯 Precisión: {gps.accuracy}m")
    
    # Verificar sello
    is_valid = ForensicHashService.verify_forensic_seal(
        original_seal=seal,
        file_content=file_content,
        gps_coords=gps,
        tenant_id=1,
        uploaded_by=42,
        metadata={"task_code": "ATA-71-001"}
    )
    
    print(f"\n{'✅' if is_valid else '❌'} Verificación: {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
