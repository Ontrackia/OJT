# Autenticación con GitHub - Guía Rápida

## ⚠️ Problema: GitHub no acepta contraseñas

Desde agosto 2021, GitHub **NO acepta contraseñas** para operaciones Git. Necesitas usar uno de estos métodos:

---

## ✅ Opción 1: Personal Access Token (PAT) - MÁS FÁCIL

### Paso 1: Crear Token en GitHub

1. Ve a: <https://github.com/settings/tokens>
2. Click en **"Generate new token"** → **"Generate new token (classic)"**
3. Nombre: `OnTrackia OJT - Mac`
4. Selecciona permisos:
   - ✅ **repo** (todos los sub-items)
   - ✅ **workflow**
5. Click **"Generate token"**
6. **¡COPIA EL TOKEN!** (solo lo verás una vez)

### Paso 2: Usar el Token

Cuando Git te pida contraseña, **pega el token en lugar de tu contraseña**:

```bash
cd ~/Desktop/OnTrackIA_OJT
git push -u origin main

# Username: tu_usuario_github
# Password: [PEGA_TU_TOKEN_AQUÍ]
```

### Guardar Token (opcional)

Para no tenerlo que escribir cada vez:

```bash
git config --global credential.helper osxkeychain
```

---

## ✅ Opción 2: GitHub CLI (gh) - RECOMENDADO

Más fácil y seguro:

```bash
# Instalar GitHub CLI (si no lo tienes)
brew install gh

# Autenticarte
gh auth login

# Sigue las instrucciones interactivas:
# - GitHub.com
# - HTTPS
# - Authenticate Git with GitHub credentials? YES
# - Login with a web browser

# Después hacer push
cd ~/Desktop/OnTrackIA_OJT
git push -u origin main
```

---

## ✅ Opción 3: SSH Keys

### Generar SSH key

```bash
ssh-keygen -t ed25519 -C "tu_email@ejemplo.com"
# Presiona Enter para aceptar ubicación default
# Poner passphrase (opcional)

# Copiar la clave pública
cat ~/.ssh/id_ed25519.pub | pbcopy
```

### Agregar a GitHub

1. Ve a: <https://github.com/settings/keys>
2. Click **"New SSH key"**
3. Título: `Mac OnTrackia`
4. Pega la clave (ya está en clipboard)
5. Click **"Add SSH key"**

### Cambiar remote a SSH

```bash
cd ~/Desktop/OnTrackIA_OJT
git remote set-url origin git@github.com:Ontrackia/OJT.git
git push -u origin main
```

---

## 🚀 Recomendación

**Usa GitHub CLI (`gh`)** - Es lo más fácil y seguro. Solo tienes que:

```bash
brew install gh
gh auth login
git push -u origin main
```

---

## 🆘 Si tienes problemas

1. **Error: Permission denied**
   - Verifica que eres miembro de la org Ontrackia
   - Verifica permisos del repositorio OJT

2. **Error: Authentication failed**
   - Asegúrate de usar el TOKEN, no la contraseña
   - Verifica que el token tenga permisos `repo`

3. **Error: remote origin already exists**
   - Ya está configurado correctamente ✅
   - Solo falta autenticarte

---

## ✅ Estado Actual

- ✅ Repositorio local creado
- ✅ Commit inicial listo (22 archivos, 1334 líneas)
- ✅ Remote configurado: `https://github.com/Ontrackia/OJT.git`
- ⏸️ **Falta: Autenticación para hacer push**

**Siguiente paso:** Elige una opción de autenticación de arriba y ejecuta `git push -u origin main`
