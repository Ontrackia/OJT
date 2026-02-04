#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - Zero Insurrections Filter
================================================
Script de auditoría para validar nomenclatura oficial y eliminar
términos prohibidos del código base.

Protocolo: Solo se permiten términos oficiales (main, stable, verified)
Prohibidos: master, gold, beta, alpha, dev-unstable, experimental

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: Protocolo Búnker
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict

# ==========================================
# CONFIGURACIÓN
# ==========================================
ALLOWED_BRANCH_NAMES = ["main", "stable", "verified", "hotfix", "release"]
FORBIDDEN_TERMS = [
    "master", "gold", "beta", "alpha", 
    "dev-unstable", "experimental", "testing"
]

# Extensiones de archivo a auditar
CODE_EXTENSIONS = [".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".yml", ".yaml", ".json", ".sh"]

@dataclass
class ViolationReport:
    """Reporte de violación de nomenclatura"""
    file_path: str
    line_number: int
    line_content: str
    forbidden_term: str
    severity: str  # "high", "medium", "low"

class ZeroInsurrectionsAuditor:
    """
    Auditor de nomenclatura oficial
    Escanea código base buscando términos prohibidos
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.violations: List[ViolationReport] = []
        self.scanned_files = 0
        self.ignored_dirs = {
            "node_modules", "__pycache__", ".git", "dist", 
            "build", ".venv", "venv", "env"
        }
    
    def should_skip_path(self, path: Path) -> bool:
        """Determina si un path debe ser ignorado"""
        return any(ignored in path.parts for ignored in self.ignored_dirs)
    
    def scan_file(self, file_path: Path):
        """
        Escanea un archivo buscando términos prohibidos
        
        Args:
            file_path: Ruta del archivo
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, start=1):
                    line_lower = line.lower()
                    
                    for forbidden in FORBIDDEN_TERMS:
                        # Buscar término prohibido (case-insensitive)
                        if re.search(r'\b' + re.escape(forbidden) + r'\b', line_lower):
                            # Determinar severidad
                            severity = self._determine_severity(line, forbidden, file_path)
                            
                            self.violations.append(ViolationReport(
                                file_path=str(file_path.relative_to(self.root_dir)),
                                line_number=line_num,
                                line_content=line.strip()[:100],  # Limitar longitud
                                forbidden_term=forbidden,
                                severity=severity
                            ))
        except Exception as e:
            print(f"⚠️  Error escaneando {file_path}: {str(e)}")
    
    def _determine_severity(self, line: str, term: str, file_path: Path) -> str:
        """Determina la severidad de la violación"""
        # Alta: En nombres de branches, configuraciones críticas
        if any(word in line.lower() for word in ["branch", "git", "deploy", "production"]):
            return "high"
        
        # Media: En comentarios o documentación
        if line.strip().startswith("#") or line.strip().startswith("//"):
            return "medium"
        
        # Baja: En otros contextos
        return "low"
    
    def audit_project(self):
        """Audita todo el proyecto"""
        print(f"\n🔍 Escaneando proyecto: {self.root_dir}")
        print("="*60)
        
        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix in CODE_EXTENSIONS:
                if not self.should_skip_path(file_path):
                    self.scan_file(file_path)
                    self.scanned_files += 1
        
        print(f"✅ Archivos escaneados: {self.scanned_files}")
        print(f"⚠️  Violaciones encontradas: {len(self.violations)}\n")
    
    def print_report(self):
        """Imprime reporte de violaciones"""
        if not self.violations:
            print("\n✅ CERO INSURRECCIONES - Nomenclatura 100% conforme")
            print("="*60)
            return
        
        print("\n❌ REPORTE DE VIOLACIONES")
        print("="*60)
        
        # Agrupar por severidad
        by_severity = defaultdict(list)
        for v in self.violations:
            by_severity[v.severity].append(v)
        
        for severity in ["high", "medium", "low"]:
            violations = by_severity[severity]
            if not violations:
                continue
            
            severity_emoji = {"high": "🔴", "medium": "🟡", "low": "⚪"}
            print(f"\n{severity_emoji[severity]} SEVERIDAD: {severity.upper()} ({len(violations)} violaciones)")
            print("-"*60)
            
            for v in violations:
                print(f"  Archivo: {v.file_path}")
                print(f"  Línea {v.line_number}: {v.line_content}")
                print(f"  Término prohibido: '{v.forbidden_term}'")
                print()
        
        # Resumen por término
        term_counts = defaultdict(int)
        for v in self.violations:
            term_counts[v.forbidden_term] += 1
        
        print("\n📊 RESUMEN POR TÉRMINO")
        print("-"*60)
        for term, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  '{term}': {count} ocurrencias")
        
        print("\n" + "="*60)
        print(f"❌ TOTAL VIOLACIONES: {len(self.violations)}")
        print("="*60)
    
    def generate_fix_script(self, output_file: str = "fix_nomenclature.sh"):
        """
        Genera script de shell para corregir violaciones automáticamente
        
        Args:
            output_file: Nombre del archivo de script
        """
        if not self.violations:
            return
        
        replacements = {
            "master": "main",
            "gold": "stable",
            "beta": "verified",
            "alpha": "verified",
            "dev-unstable": "development",
            "experimental": "development"
        }
        
        script_lines = [
            "#!/bin/bash",
            "# Script generado automáticamente para corregir nomenclatura",
            "# OnTrackIA OJT V2.0 - Zero Insurrections",
            "",
            "echo '🔧 Corrigiendo nomenclatura prohibida...'",
            ""
        ]
        
        # Agrupar por archivo
        files_to_fix = defaultdict(list)
        for v in self.violations:
            files_to_fix[v.file_path].append(v)
        
        for file_path, violations in files_to_fix.items():
            script_lines.append(f"# Archivo: {file_path}")
            for v in violations:
                replacement = replacements.get(v.forbidden_term, "main")
                script_lines.append(
                    f"sed -i '' 's/\\b{v.forbidden_term}\\b/{replacement}/gi' {file_path}"
                )
            script_lines.append("")
        
        script_lines.append("echo '✅ Corrección completada'")
        
        output_path = self.root_dir / output_file
        with open(output_path, 'w') as f:
            f.write('\n'.join(script_lines))
        
        os.chmod(output_path, 0o755)
        print(f"\n📝 Script de corrección generado: {output_file}")
    
    def has_violations(self) -> bool:
        """Retorna True si hay violaciones"""
        return len(self.violations) > 0

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Zero Insurrections Filter")
    parser.add_argument("--path", default=".", help="Ruta del proyecto a auditar")
    parser.add_argument("--fix", action="store_true", help="Generar script de corrección")
    parser.add_argument("--strict", action="store_true", help="Modo estricto (exit code 1 si hay violaciones)")
    
    args = parser.parse_args()
    
    # Ejecutar auditoría
    auditor = ZeroInsurrectionsAuditor(args.path)
    auditor.audit_project()
    auditor.print_report()
    
    # Generar script de corrección si se solicita
    if args.fix and auditor.has_violations():
        auditor.generate_fix_script()
    
    # Exit code
    if args.strict and auditor.has_violations():
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
