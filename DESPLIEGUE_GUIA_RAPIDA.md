# 🚀 Guía Rápida de Despliegue - Backend API CarroIoT

## 📋 Pre-requisitos en EC2 Windows Server

1. **Python 3.11+** instalado y en PATH
2. **Git** instalado (opcional, puedes copiar archivos manualmente)
3. **Acceso RDP** a la instancia EC2
4. **Security Group** configurado:
   - Puerto **5500** (TCP) abierto para 0.0.0.0/0
   - Puerto **3389** (TCP) para RDP
   - Puerto **3306** (TCP) para RDS MySQL (si necesitas conectarte directamente)

## 📁 Archivos de Despliegue Incluidos

En la carpeta `backend-api/` ya están todos los archivos necesarios:

✅ **setup.bat** - Script de instalación automática
✅ **start.bat** - Script de inicio rápido del servidor
✅ **.env** - Configuración de producción con credenciales RDS
✅ **requirements.txt** - Dependencias Python
✅ **init_database.sql** - Script SQL para inicializar base de datos
✅ **src/app.py** - Aplicación principal (8 errores de linter CORREGIDOS)

## 🔧 Instalación (Paso a Paso)

### Opción A: Instalación Automática (Recomendada)

```powershell
# 1. Clonar o copiar el proyecto a la máquina EC2
cd C:\
git clone https://github.com/AngelLugo-Dev/API-Carro-IoT.git
# O descomprimir zip si se transfirió manualmente

# 2. Ir a la carpeta backend
cd C:\API-Carro-IoT\backend-api

# 3. Ejecutar setup automático
.\setup.bat

# 4. Iniciar el servidor
.\start.bat
```

### Opción B: Instalación Manual

```powershell
# 1. Verificar Python
python --version
# Debe mostrar: Python 3.11.x o superior

# 2. Crear entorno virtual
cd C:\API-Carro-IoT\backend-api
python -m venv venv

# 3. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 4. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 5. Verificar que .env existe con credenciales correctas
type .env

# 6. Iniciar servidor
cd src
python app.py
```

## 🗄️ Inicialización de Base de Datos

**IMPORTANTE**: Ejecutar solo la primera vez o cuando se necesite resetear.

```powershell
# Conectar a RDS MySQL desde EC2 o desde MySQL Workbench
mysql -h instancia-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com -P 3306 -u admin -p

# Cuando pida password: Admin12345#!

# Ejecutar script de inicialización
source C:\API-Carro-IoT\backend-api\init_database.sql

# O copiar/pegar el contenido del archivo SQL directamente
```

## 🔐 Configuración de Credenciales

El archivo `.env` ya está configurado con las credenciales de producción:

```ini
# Base de datos RDS AWS
DB_HOST=instancia-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=Admin12345#!
DB_NAME=carrito_iot

# Servidor API
PORT=5500
HOST=0.0.0.0

# Ambiente
FLASK_ENV=production
CORS_ORIGINS=*
```

**NO MODIFICAR** a menos que cambien las credenciales de AWS.

## ✅ Verificación de Funcionamiento

### Test 1: Health Check Local

```powershell
# Desde PowerShell en EC2
curl http://localhost:5500/api/health
```

**Respuesta esperada:**

```json
{
  "api": "healthy",
  "database": "connected",
  "timestamp": "2025-10-27T..."
}
```

### Test 2: Health Check Remoto

```powershell
# Desde tu computadora local (reemplaza con IP pública de EC2)
curl http://54.123.45.67:5500/api/health
```

### Test 3: WebSocket Connection

```javascript
// Desde consola del navegador en https://angellugo-dev.github.io/frontend-web-iot/
// Verificar que aparece: 🟢 Conectado
```

## 🔄 Configurar como Servicio Windows (NSSM)

Para que el servidor inicie automáticamente:

```powershell
# 1. Descargar NSSM
# Ir a: https://nssm.cc/download
# Descargar nssm-2.24.zip
# Extraer a C:\nssm

# 2. Instalar servicio
C:\nssm\win64\nssm.exe install CarroIoTAPI

# En la ventana que aparece:
# - Path: C:\API-Carro-IoT\backend-api\venv\Scripts\python.exe
# - Startup directory: C:\API-Carro-IoT\backend-api\src
# - Arguments: app.py

# 3. Iniciar servicio
net start CarroIoTAPI

# 4. Verificar estado
nssm status CarroIoTAPI
```

## 🐛 Solución de Problemas Comunes

### Problema: "python no se reconoce como comando"

**Solución:**

```powershell
# Agregar Python al PATH manualmente
$env:Path += ";C:\Python311;C:\Python311\Scripts"
```

### Problema: "No module named 'flask'"

**Solución:**

```powershell
# Asegúrate de estar en el entorno virtual
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Problema: "Database connection failed"

**Solución:**

1. Verificar que el Security Group de RDS permite conexiones desde EC2
2. Verificar credenciales en `.env`
3. Ping al host RDS:

```powershell
Test-NetConnection -ComputerName instancia-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com -Port 3306
```

### Problema: "Address already in use: 5500"

**Solución:**

```powershell
# Encontrar proceso usando el puerto
netstat -ano | findstr :5500

# Terminar el proceso (reemplaza PID)
taskkill /PID 1234 /F
```

### Problema: "CORS error desde frontend"

**Solución:**

- Verificar que `CORS_ORIGINS=*` esté en `.env`
- Verificar que el Security Group permite tráfico desde 0.0.0.0/0 en puerto 5500
- Reiniciar el servidor después de cambios

## 📊 Monitoreo y Logs

### Ver logs en tiempo real:

```powershell
# Si se ejecuta con start.bat
# Los logs aparecen directamente en la consola

# Si se ejecuta como servicio NSSM
# Revisar logs en:
type C:\API-Carro-IoT\backend-api\src\app.log
```

### Comandos útiles:

```powershell
# Ver procesos Python activos
Get-Process python

# Verificar uso de puerto
netstat -ano | findstr :5500

# Test de conectividad RDS
Test-NetConnection -ComputerName instancia-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com -Port 3306

# Verificar IP pública de EC2
curl http://checkip.amazonaws.com
```

## 🔗 Integración con Frontend

Una vez que el backend esté corriendo:

1. **Obtener IP pública de EC2:**

```powershell
curl http://checkip.amazonaws.com
```

2. **Actualizar frontend (desde repositorio local):**

```javascript
// En frontend-web/js/config.js
// Reemplazar localhost con la IP de EC2:
const API_BASE_URL = "http://54.123.45.67:5500";
const WEBSOCKET_URL = "http://54.123.45.67:5500";
```

3. **Commit y push:**

```bash
git add frontend-web/js/config.js
git commit -m "Update: Production API URL"
git push origin master
```

4. **GitHub Pages se actualizará automáticamente** en 1-2 minutos

## 📝 Notas Importantes

### Errores de Pylance (Linter)

El archivo `app.py` tiene 2 advertencias del linter que **SON FALSOS POSITIVOS**:

- `request.sid` - Existe en runtime con Flask-SocketIO
- Estos errores NO afectan el funcionamiento

### Arquitectura Validada

✅ Modelo-Controlador (models/, controllers/)
✅ WebSocket PUSH (14 eventos bidireccionales)
✅ CORS para todas las IPs (origins="\*")
✅ Puerto 5500 configurado
✅ Compatible con EC2 Windows Server
✅ Conectado a RDS MySQL
✅ Integrado con GitHub Pages

## 🎯 Checklist de Despliegue

- [ ] Python 3.11+ instalado en EC2
- [ ] Security Group puerto 5500 abierto
- [ ] Proyecto copiado a C:\API-Carro-IoT\
- [ ] Ejecutado `setup.bat`
- [ ] Verificado `.env` con credenciales correctas
- [ ] Inicializada base de datos con `init_database.sql`
- [ ] Ejecutado `start.bat`
- [ ] Health check exitoso (http://localhost:5500/api/health)
- [ ] Health check remoto exitoso (http://IP_PUBLICA:5500/api/health)
- [ ] Configurado servicio NSSM (opcional pero recomendado)
- [ ] IP pública obtenida y documentada
- [ ] Frontend actualizado con IP de EC2
- [ ] Test de WebSocket desde frontend (🟢 Conectado)

## 📞 Contacto y Soporte

Para problemas de despliegue:

1. Revisar logs del servidor
2. Verificar Security Groups en AWS Console
3. Verificar credenciales RDS
4. Consultar documento completo: `DEPLOY_EC2_WINDOWS.md`

---

**Última actualización:** 27 de octubre de 2025
**Versión:** 1.0.0
**Estado:** Listo para producción ✅
