# Protocolo de 'Prudencia Total': Verificación Pre-Despliegue

Este protocolo establece los pasos mandatorios de verificación manual que deben realizarse antes de transferir el paquete de despliegue al servidor de producción. La precisión prima sobre la velocidad.

## 📂 1. Verificación Física en Carpeta Local

Antes de realizar el empaquetado final, se debe verificar físicamente la existencia y corrección de los siguientes archivos críticos en la carpeta del escritorio `OnTrackIA_OJT`:

| Ubicación | Archivo | Función Crítica |
| :--- | :--- | :--- |
| **Raíz (/)** | `README.md` | Contiene el Walkthrough consolidado y manual de despliegue. |
| **backend/api/app/resources/** | `rbac_matrix.csv` | Matriz de permisos dinámica para el control de firmas. |
| **backend/api/app/services/** | `verify_ai.py` | Script de gobernanza para auditoría de salud de la IA. |
| **docs/** | `CONFIGURACION_MULTI_LLM.md` | Parámetros de configuración para el modelo Mistral/OACI. |
| **frontend/src/** | `purple.css` | Define la identidad visual **Morado Oscuro** (#0a051a). |

## 📦 2. Auditoría del Contenido del ZIP

Una vez generado el archivo `OnTrackIA_OJT.zip`, no se debe confiar ciegamente en el comando de compresión. Se debe inspeccionar el contenido sin descomprimir utilizando el "Truco de Auditoría":

```bash
unzip -l ~/Desktop/OnTrackIA_OJT.zip
```

**Lista de comprobación (Checklist):**

- [ ] No existen carpetas `.git`, `node_modules` o `venv`.
- [ ] La estructura de directorios (`backend/`, `frontend/`, `automation/`, `docs/`) es plana y correcta.
- [ ] El tamaño del archivo es consistente con el contenido esperado (~15-50MB dependiendo de los assets).

## 🛡️ 3. Verificación de Identidad Visual (Búnker)

Como el sistema de login debe ser un búnker inexpugnable, se debe verificar que la configuración del frontend apunte correctamente a los estilos de branding aprobados:

- **Ruta**: `frontend/src/`
- **Archivos**: `index.css`, `purple.css` o archivos de configuración de tema.
- **Validación**: Asegurar que el color de fondo coincida con `#0a051a` para garantizar una transición de marca inmediata tras la subida.

### Certificación Final

*"Un segundo de verificación ahorra horas de corrección en el servidor."*
