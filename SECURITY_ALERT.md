# 🚨 SECURITY ALERT - Exposed API Key Remediation

**Date:** 2026-02-04  
**Issue:** Mistral AI API key exposed in GitHub repository  
**Detected by:** GitGuardian

---

## ⚠️ IMMEDIATE ACTIONS REQUIRED

### **1. Revoke Exposed API Key**

La clave expuesta fue: `c3ko2dPmh4XTPSEZAz058KsS8W22RXMH`

**ACCIÓN INMEDIATA:**

1. Ve a: <https://console.mistral.ai/api-keys/>
2. Revoca la clave expuesta
3. Genera una nueva clave API
4. Guárdala en un lugar seguro (1Password, Bitwarden, etc.)

### **2. Actualizar Variables de Entorno**

**En tu servidor Hetzner:**

```bash
# Conectar al servidor
ssh root@TU_IP_SERVIDOR

# Editar archivo .env
cd /opt/ontrackia/OJT/backend
nano .env

# Actualizar con la NUEVA clave
MISTRAL_API_KEY=tu_nueva_clave_aqui

# Reiniciar servicio
sudo systemctl restart ontrackia-backend
```

**En GitHub Secrets (si usas GitHub Actions):**

1. Ve a: <https://github.com/Ontrackia/OJT/settings/secrets/actions>
2. Edita `MISTRAL_API_KEY`
3. Pega la nueva clave
4. Guarda

### **3. Verificar que NO Hay Más Secretos Expuestos**

```bash
cd /Users/gregorioromerovega/Desktop/OnTrackIA_OJT

# Buscar posibles secretos
grep -r "API_KEY" --exclude-dir=.git --exclude-dir=node_modules
grep -r "PASSWORD" --exclude-dir=.git --exclude-dir=node_modules
grep -r "SECRET" --exclude-dir=.git --exclude-dir=node_modules
```

---

## ✅ CAMBIOS APLICADOS

1. ✅ Removida clave de `DEPLOYMENT_CHECKLIST.md`
2. ✅ Removida clave de `DEPLOYMENT.md`
3. ✅ Actualizado `.gitignore` para prevenir futuros leaks
4. ✅ Creado `.env.example` sin secretos reales

---

## 🔒 PREVENCIÓN FUTURA

### **Usar Variables de Entorno SIEMPRE**

**NUNCA hacer:**

```python
# ❌ MAL
api_key = "c3ko2dPmh4XTPSEZAz058KsS8W22RXMH"
```

**SIEMPRE hacer:**

```python
# ✅ BIEN
import os
api_key = os.getenv("MISTRAL_API_KEY")
```

### **Verificar Antes de Commit**

```bash
# Antes de cada commit
git diff --cached | grep -i "api_key\|password\|secret"

# Si encuentra algo, NO HACER COMMIT
```

### **Usar pre-commit hooks**

```bash
# Instalar pre-commit
pip install pre-commit

# Crear .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Instalar hooks
pre-commit install
```

---

## 📋 CHECKLIST DE REMEDIACIÓN

- [ ] Clave expuesta revocada en Mistral AI
- [ ] Nueva clave generada
- [ ] `.env` actualizado en servidor
- [ ] GitHub Secrets actualizado
- [ ] Servicio backend reiniciado
- [ ] Verificado que no hay más secretos
- [ ] Commit de limpieza pushed a GitHub
- [ ] GitGuardian alert cerrado

---

## 🎯 PRÓXIMOS PASOS

1. **Revocar clave inmediatamente**
2. **Generar nueva clave**
3. **Actualizar en servidor y GitHub**
4. **Commit y push de limpieza**
5. **Verificar que GitGuardian cierra el alert**

---

**IMPORTANTE:** Esta clave ya está comprometida. Debe ser revocada INMEDIATAMENTE aunque no se haya usado maliciosamente aún.
