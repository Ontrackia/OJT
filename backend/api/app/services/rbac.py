#!/usr/bin/env python3
"""
OnTrackIA OJT V2.0 - RBAC Service
==================================
Servicio de control de acceso basado en roles (RBAC) con
jerarquía Individual vs Empresa.

Roles soportados:
- admin: Control total de la organización
- supervisor: Valida tareas de su departamento
- technician: Registra y sube evidencias propias
- individual_user: Configura su plan y threshold propios
- company_user: Usuario de empresa (threshold controlado por admin)
- company_admin: Admin de empresa (controla thresholds de usuarios)
- auditor: Solo lectura y reportes
- guest: Acceso público limitado

Autor: OnTrackia Dev Team
Fecha: 2026-02-04
Compliance: Protocolo Búnker
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PermissionType(str, Enum):
    """Tipos de permisos"""
    ALLOW = "allow"
    DENY = "deny"

class ScopeType(str, Enum):
    """Tipos de alcance"""
    ORGANIZATION = "organization"
    DEPARTMENT = "department"
    OWN = "own"
    PUBLIC = "public"

@dataclass
class RBACRule:
    """Regla RBAC"""
    role: str
    resource: str
    action: str
    permission: PermissionType
    scope: ScopeType

class RBACService:
    """
    Servicio de control de acceso RBAC
    """
    
    def __init__(self, matrix_path: str = "./rbac_matrix.csv"):
        self.matrix_path = Path(matrix_path)
        self.rules: List[RBACRule] = []
        self.load_matrix()
    
    def load_matrix(self):
        """Carga la matriz RBAC desde CSV"""
        if not self.matrix_path.exists():
            raise FileNotFoundError(f"RBAC matrix not found: {self.matrix_path}")
        
        with open(self.matrix_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rule = RBACRule(
                    role=row['role'],
                    resource=row['resource'],
                    action=row['action'],
                    permission=PermissionType(row['permission']),
                    scope=ScopeType(row['scope'])
                )
                self.rules.append(rule)
        
        print(f"✅ Loaded {len(self.rules)} RBAC rules from {self.matrix_path}")
    
    def check_permission(
        self,
        user_role: str,
        resource: str,
        action: str,
        user_id: Optional[int] = None,
        resource_owner_id: Optional[int] = None,
        user_department: Optional[str] = None,
        resource_department: Optional[str] = None
    ) -> bool:
        """
        Verifica si un rol tiene permiso para una acción
        
        Args:
            user_role: Rol del usuario
            resource: Recurso a acceder
            action: Acción a realizar
            user_id: ID del usuario
            resource_owner_id: ID del dueño del recurso
            user_department: Departamento del usuario
            resource_department: Departamento del recurso
        
        Returns:
            True si tiene permiso, False si no
        """
        # Buscar reglas aplicables
        applicable_rules = [
            rule for rule in self.rules
            if (rule.role == user_role or rule.role == "all") and
               (rule.resource == resource or rule.resource == "all") and
               (rule.action == action or rule.action == "all")
        ]
        
        # Si no hay reglas, denegar por defecto
        if not applicable_rules:
            return False
        
        # Evaluar cada regla
        for rule in applicable_rules:
            # Verificar alcance
            if rule.scope == ScopeType.ORGANIZATION:
                # Alcance de organización: siempre aplica
                if rule.permission == PermissionType.DENY:
                    return False
                elif rule.permission == PermissionType.ALLOW:
                    return True
            
            elif rule.scope == ScopeType.DEPARTMENT:
                # Alcance de departamento: verificar departamento
                if user_department and resource_department:
                    if user_department == resource_department:
                        if rule.permission == PermissionType.DENY:
                            return False
                        elif rule.permission == PermissionType.ALLOW:
                            return True
            
            elif rule.scope == ScopeType.OWN:
                # Alcance propio: verificar ownership
                if user_id and resource_owner_id:
                    if user_id == resource_owner_id:
                        if rule.permission == PermissionType.DENY:
                            return False
                        elif rule.permission == PermissionType.ALLOW:
                            return True
            
            elif rule.scope == ScopeType.PUBLIC:
                # Alcance público: siempre aplica
                if rule.permission == PermissionType.DENY:
                    return False
                elif rule.permission == PermissionType.ALLOW:
                    return True
        
        # Por defecto, denegar
        return False
    
    def can_adjust_threshold(
        self,
        user_role: str,
        user_id: int,
        target_user_id: int,
        is_individual_plan: bool
    ) -> bool:
        """
        Verifica si un usuario puede ajustar el threshold de otro
        
        Args:
            user_role: Rol del usuario
            user_id: ID del usuario que quiere ajustar
            target_user_id: ID del usuario objetivo
            is_individual_plan: Si el plan es individual o empresarial
        
        Returns:
            True si puede ajustar, False si no
        """
        # Si es plan individual y es su propio threshold
        if is_individual_plan and user_id == target_user_id:
            return self.check_permission(
                user_role='individual_user',
                resource='threshold',
                action='adjust',
                user_id=user_id,
                resource_owner_id=target_user_id
            )
        
        # Si es plan empresarial, solo company_admin puede ajustar
        if not is_individual_plan:
            return self.check_permission(
                user_role='company_admin',
                resource='threshold',
                action='adjust'
            )
        
        return False
    
    def get_allowed_actions(self, user_role: str, resource: str) -> List[str]:
        """
        Obtiene las acciones permitidas para un rol y recurso
        
        Args:
            user_role: Rol del usuario
            resource: Recurso
        
        Returns:
            Lista de acciones permitidas
        """
        allowed_actions = []
        
        for rule in self.rules:
            if (rule.role == user_role or rule.role == "all") and \
               (rule.resource == resource or rule.resource == "all"):
                if rule.permission == PermissionType.ALLOW:
                    if rule.action == "all":
                        allowed_actions.append("*")
                    else:
                        allowed_actions.append(rule.action)
        
        return list(set(allowed_actions))
    
    def print_role_permissions(self, role: str):
        """Imprime los permisos de un rol"""
        print(f"\n📋 Permisos para rol: {role}")
        print("="*60)
        
        role_rules = [rule for rule in self.rules if rule.role == role]
        
        if not role_rules:
            print("  ⚠️ No hay reglas definidas para este rol")
            return
        
        for rule in role_rules:
            emoji = "✅" if rule.permission == PermissionType.ALLOW else "❌"
            print(f"  {emoji} {rule.resource}.{rule.action} ({rule.scope})")

# Ejemplo de uso
if __name__ == "__main__":
    rbac = RBACService()
    
    print("\n🔐 OnTrackIA OJT V2.0 - RBAC Service")
    print("="*60)
    
    # Test 1: Usuario individual ajustando su propio threshold
    can_adjust = rbac.check_permission(
        user_role='individual_user',
        resource='threshold',
        action='adjust',
        user_id=1,
        resource_owner_id=1
    )
    print(f"\n1. Individual user ajustando threshold propio: {'✅ PERMITIDO' if can_adjust else '❌ DENEGADO'}")
    
    # Test 2: Usuario de empresa ajustando threshold (debe fallar)
    can_adjust = rbac.check_permission(
        user_role='company_user',
        resource='threshold',
        action='adjust',
        user_id=2,
        resource_owner_id=2
    )
    print(f"2. Company user ajustando threshold: {'✅ PERMITIDO' if can_adjust else '❌ DENEGADO'}")
    
    # Test 3: Company admin ajustando threshold de cualquier usuario
    can_adjust = rbac.check_permission(
        user_role='company_admin',
        resource='threshold',
        action='adjust'
    )
    print(f"3. Company admin ajustando threshold: {'✅ PERMITIDO' if can_adjust else '❌ DENEGADO'}")
    
    # Test 4: Técnico validando su propia tarea (debe fallar)
    can_validate = rbac.check_permission(
        user_role='technician',
        resource='task',
        action='validate',
        user_id=3,
        resource_owner_id=3
    )
    print(f"4. Technician validando tarea propia: {'✅ PERMITIDO' if can_validate else '❌ DENEGADO'}")
    
    # Test 5: Supervisor validando tarea de su departamento
    can_validate = rbac.check_permission(
        user_role='supervisor',
        resource='task',
        action='validate',
        user_department='maintenance',
        resource_department='maintenance'
    )
    print(f"5. Supervisor validando tarea del departamento: {'✅ PERMITIDO' if can_validate else '❌ DENEGADO'}")
    
    # Mostrar permisos de cada rol
    for role in ['admin', 'individual_user', 'company_user', 'company_admin', 'technician']:
        rbac.print_role_permissions(role)
