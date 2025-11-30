# 🌱 BloomJoy - Guía de Despliegue en Railway

## 📋 Preparación completada ✅

Los siguientes archivos han sido actualizados para Railway:
- ✅ `backend/requirements.txt` - Dependencias de Flask + Gunicorn
- ✅ `backend/Procfile` - Configuración de inicio
- ✅ `backend/app.py` - Usando variables de entorno
- ✅ `dashboard/requirements.txt` - Dependencias de Streamlit
- ✅ `dashboard/diseno.py` - Usando variables de entorno
- ✅ `.gitignore` - Archivos excluidos del repositorio

---

## 🚂 Pasos para desplegar en Railway

### 1️⃣ Crear cuenta en Railway
1. Ve a https://railway.app
2. Regístrate con tu cuenta de GitHub
3. Autoriza el acceso a tus repositorios

### 2️⃣ Desplegar MySQL Database
1. En Railway Dashboard, haz clic en **"New Project"**
2. Selecciona **"Provision MySQL"**
3. Espera a que se cree la base de datos
4. Haz clic en la base de datos → pestaña **"Variables"**
5. **Copia estas credenciales** (las necesitarás después):
   - `MYSQL_HOST`
   - `MYSQL_USER` 
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`
   - `MYSQL_PORT`

### 3️⃣ Importar tu esquema de base de datos
1. En Railway, haz clic en tu MySQL → pestaña **"Data"**
2. Copia la **Connection URL** (formato: `mysql://user:pass@host:port/database`)
3. En tu computadora, exporta tu base de datos actual:
   ```bash
   mysqldump -u root -p reto_db > schema.sql
   ```
4. Importa a Railway usando un cliente MySQL (MySQL Workbench, DBeaver, etc.):
   - Conecta usando las credenciales de Railway
   - Ejecuta el archivo `schema.sql`

mysql://root:acRTgBfoqEUPTdjCJJtkdhzoKPajvlxd@interchange.proxy.rlwy.net:48378/railway

### 4️⃣ Desplegar Backend (Flask)
1. En Railway, haz clic en **"New"** → **"GitHub Repo"**
2. Selecciona tu repositorio **`BloomJoy`**
3. Railway detectará el proyecto automáticamente
4. Haz clic en el servicio → **"Settings"**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Ve a la pestaña **"Variables"** y agrega:
   ```
   MYSQL_HOST=<tu-host-de-railway>
   MYSQL_USER=<tu-usuario>
   MYSQL_PASSWORD=<tu-password>
   MYSQL_DATABASE=<tu-database>
   MYSQL_PORT=<tu-puerto>
   ```
6. Haz clic en **"Deploy"**
7. Espera a que termine el despliegue
8. En **"Settings"** → **"Networking"**, copia la URL pública (ej: `https://bloomjoy-backend-production.up.railway.app`)

### 5️⃣ Desplegar Dashboard (Streamlit)
1. En el mismo proyecto de Railway, haz clic en **"New"** → **"GitHub Repo"**
2. Selecciona nuevamente tu repositorio **`BloomJoy`**
3. Haz clic en el nuevo servicio → **"Settings"**:
   - **Root Directory**: `dashboard`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run diseno.py --server.port=$PORT --server.address=0.0.0.0`
4. Ve a la pestaña **"Variables"** y agrega las mismas variables de MySQL:
   ```
   MYSQL_HOST=<tu-host-de-railway>
   MYSQL_USER=<tu-usuario>
   MYSQL_PASSWORD=<tu-password>
   MYSQL_DATABASE=<tu-database>
   MYSQL_PORT=<tu-puerto>
   ```
5. Haz clic en **"Deploy"**
6. En **"Settings"** → **"Networking"**, copia la URL pública del dashboard

### 6️⃣ Actualizar ESP32
1. Abre tu archivo `sensors.ino`
2. Cambia la URL del servidor:
   ```cpp
   // Antes:
   String serverBase = "http://172.20.10.4";
   
   // Después (usa tu URL de Railway):
   String serverBase = "https://bloomjoy-backend-production.up.railway.app";
   ```
3. Sube el código actualizado a tu ESP32

---

## 🔍 Verificación

### Probar el Backend:
```bash
curl https://tu-backend-url.railway.app/config/1
```
Deberías recibir la configuración de la planta en JSON.

### Probar el Dashboard:
Abre la URL del dashboard en tu navegador. Deberías ver el dashboard de BloomJoy funcionando.

### Probar ESP32:
El ESP32 debería enviar datos automáticamente cada 15 segundos a la URL de Railway.

---

## 🐛 Solución de problemas

### Error: "No module named 'dotenv'"
- Verifica que `python-dotenv` esté en `requirements.txt`
- Redeploy el servicio

### Error de conexión a MySQL:
- Verifica que todas las variables de entorno estén configuradas correctamente
- Verifica que el `MYSQL_PORT` sea un número (usualmente 3306)
- Revisa los logs en Railway → pestaña "Deployments"

### Dashboard no carga imágenes:
- Asegúrate de que `bloomjoy.jpeg` y `samuel.png` estén en la carpeta `dashboard/`
- Sube los archivos al repositorio de GitHub

### ESP32 no puede enviar datos:
- Verifica que la URL sea HTTPS (Railway usa SSL por defecto)
- Si tu ESP32 no soporta HTTPS, necesitarás configurar certificados SSL

---

## 📊 Monitoreo

En Railway puedes:
- **Ver logs en tiempo real**: Pestaña "Deployments" → "View Logs"
- **Métricas de uso**: CPU, memoria, ancho de banda
- **Reiniciar servicios**: Botón "Restart" si algo falla

---

## 💰 Costos

Railway ofrece:
- **$5 de crédito gratis mensual** (Hobby plan)
- Suficiente para proyectos pequeños/medianos
- MySQL, Backend y Dashboard pueden correr dentro del plan gratuito

---

## ✅ Checklist Final

- [ ] MySQL desplegado en Railway
- [ ] Base de datos importada con esquema completo
- [ ] Backend desplegado y respondiendo en `/config/1`
- [ ] Dashboard desplegado y visible en navegador
- [ ] Variables de entorno configuradas en ambos servicios
- [ ] ESP32 actualizado con nueva URL
- [ ] ESP32 enviando datos correctamente
- [ ] Dashboard mostrando datos en tiempo real

---

🎉 **¡Proyecto desplegado exitosamente!**

URLs finales:
- **Backend**: `https://tu-backend.railway.app`
- **Dashboard**: `https://tu-dashboard.railway.app`
- **MySQL**: Acceso privado solo desde servicios de Railway