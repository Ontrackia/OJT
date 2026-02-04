# Comandos para Conectar con GitHub

## Paso 1: Agregar Repositorio Remoto

Reemplaza `TU_USUARIO_GITHUB` con tu usuario de GitHub:

```bash
cd ~/Desktop/OnTrackIA_OJT
git remote add origin https://github.com/TU_USUARIO_GITHUB/OJT.git
```

## Paso 2: Push al Repositorio

```bash
git push -u origin main
```

Si te pide autenticación, necesitarás tu Personal Access Token de GitHub (no tu contraseña).

## Paso 3: Verificar

```bash
git remote -v
```

Debería mostrar:

```
origin  https://github.com/TU_USUARIO_GITHUB/OJT.git (fetch)
origin  https://github.com/TU_USUARIO_GITHUB/OJT.git (push)
```

---

## Alternativa: Si ya conoces tu usuario

```bash
# Ejemplo con usuario "gregorioromero" (reemplaza con tu usuario real)
cd ~/Desktop/OnTrackIA_OJT
git remote add origin https://github.com/gregorioromero/OJT.git
git push -u origin main
```

---

## ✅ Commit Creado

Ya se creó el commit inicial con:

- **22 archivos**
- **1,334 líneas de código**
- Backend (modelos + router)
- Frontend (OJTPage.jsx)
- Documentación completa
- Archivos de configuración

**Solo falta conectar con GitHub y hacer push!**
