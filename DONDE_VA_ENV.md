# 🔧 GUÍA VISUAL: ¿Dónde va el archivo .env?

## 📁 Estructura de archivos

```
TU PC (Windows) - C:\Users\hannm\OneDrive\Escritorio\CarroIoT\
│
└── backend-api/
    ├── .env.example                    ← ✅ ESTE SÍ EXISTE (plantilla)
    ├── .env.production.example         ← ✅ ESTE SÍ EXISTE (plantilla)
    ├── .env                            ← ❌ ESTE NO EXISTE (y está bien)
    │                                      NO lo crees aquí, no sirve
    │                                      Solo se crea EN EC2
    ├── requirements.txt
    ├── init_database.sql
    └── src/
        └── app.py


TU EC2 (Linux) - /home/ubuntu/CarroIoT/
│
└── backend-api/
    ├── .env.example                    ← Copiado de GitHub
    ├── .env.production.example         ← Copiado de GitHub
    ├── .env                            ← ✅ ESTE LO CREARÁS TÚ AQUÍ
    │                                      CON TUS CREDENCIALES REALES
    ├── requirements.txt
    └── src/
        └── app.py
```

---

## 🎯 Flujo Completo

### PASO 1: En tu PC (AHORA)

```powershell
# 1. Ir a tu proyecto
cd C:\Users\hannm\OneDrive\Escritorio\CarroIoT

# 2. Subir TODO a GitHub (los .env.example SÍ se suben)
git add .
git commit -m "Initial commit"
git push origin main
```

✅ Los archivos `.env.example` **SÍ se suben a GitHub** (son plantillas sin datos reales)
❌ El archivo `.env` **NUNCA se sube** (tiene tus passwords)

---

### PASO 2: En EC2 (CUANDO LO DESPLIEGUES)

```bash
# 1. Conectar a EC2
ssh -i "tu-key.pem" ubuntu@tu-ip-ec2

# 2. Clonar repo
git clone https://github.com/TU_USUARIO/CarroIoT.git
cd CarroIoT/backend-api

# 3. AQUÍ CREAS EL ARCHIVO .env MANUALMENTE
nano .env

# 4. Dentro del editor nano, pegas esto (CON TUS DATOS):
# ↓↓↓ Copia desde aquí ↓↓↓
DB_HOST=carrito-iot-cluster.cluster-abc123.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=MiPasswordSeguro123
DB_NAME=carrito_iot

FLASK_ENV=production
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
PORT=5500
HOST=0.0.0.0
CORS_ORIGINS=*
# ↑↑↑ Hasta aquí ↑↑↑

# 5. Guardar:
#    - Presiona: Ctrl + O (guardar)
#    - Presiona: Enter (confirmar nombre)
#    - Presiona: Ctrl + X (salir)

# 6. Verificar que se creó:
ls -la
# Deberías ver: .env (con permisos -rw-r--r--)

# 7. Verificar contenido:
cat .env
# Deberías ver tus credenciales
```

---

## 🔐 ¿Cómo obtener los valores para .env?

### DB_HOST

```
AWS Console → RDS → Databases → Click en tu cluster Aurora
Tab: "Connectivity & security"
Busca: "Endpoint" (Writer instance)
```

**Ejemplo:** `carrito-iot.cluster-abc123xyz.us-east-1.rds.amazonaws.com`

### DB_USER

```
Es el "Master username" que configuraste al crear Aurora
Usualmente: admin
```

### DB_PASSWORD

```
La contraseña que elegiste al crear el cluster Aurora
```

⚠️ Si la olvidaste:

```
AWS Console → RDS → Tu cluster → Modify → "New master password"
```

### DB_NAME

```
Si tu BD ya está creada, usa el nombre que tiene
Si seguiste los ejemplos: carrito_iot
```

Para verificar:

```bash
# Desde EC2:
mysql -h tu-aurora.rds.amazonaws.com -u admin -p
# Ingresa password cuando lo pida

# Dentro de MySQL:
SHOW DATABASES;
# Deberías ver: carrito_iot (o el nombre que le pusiste)
```

### SECRET_KEY

Genera una clave aleatoria:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado y pégalo en `SECRET_KEY=...`

---

## ❓ FAQ

### ¿Por qué no crear .env en mi PC?

Porque tu PC **no tiene Aurora RDS**. El archivo `.env` solo tiene sentido **en el servidor EC2** que sí puede conectarse a Aurora.

### ¿Puedo usar .env.example o .env.production.example?

**NO**. Son solo plantillas de referencia. Debes crear `.env` (sin `.example`) con tus datos reales.

### ¿La BD ya está creada en mi instancia Aurora?

Si ya creaste las tablas manualmente en Aurora, entonces:

- ✅ **NO ejecutes** `init_database.sql`
- ✅ Solo crea el `.env` con el nombre de tu BD existente

Para verificar:

```bash
mysql -h tu-aurora.rds.amazonaws.com -u admin -p -e "USE carrito_iot; SHOW TABLES;"
```

Si ves tablas como `devices`, `device_events`, etc. → **BD lista, skip `init_database.sql`**

Si da error "Unknown database" → **Necesitas ejecutar `init_database.sql`**

### ¿Qué pasa si subo .env a GitHub por error?

🚨 **PELIGRO**: Tus credenciales estarían públicas.

Si pasa:

1. Borra el archivo del repo: `git rm --cached .env`
2. Commit: `git commit -m "Remove .env"`
3. Push: `git push`
4. **CAMBIA TUS PASSWORDS de Aurora inmediatamente**

Pero tranquilo: `.gitignore` ya lo está bloqueando, es casi imposible que pase.

---

## ✅ Checklist

**En tu PC (ahora):**

- [ ] No crear archivo `.env` aquí
- [ ] Subir código a GitHub (con `.env.example`)
- [ ] Editar `frontend-web/js/config.js` con IP de EC2

**En EC2 (cuando despliegues):**

- [ ] Clonar repo desde GitHub
- [ ] Crear archivo `.env` manualmente con `nano .env`
- [ ] Pegar configuración con credenciales reales
- [ ] Verificar conexión a Aurora
- [ ] Instalar dependencias: `pip install -r requirements.txt`
- [ ] Correr: `python src/app.py`

---

**Resumen:** El `.env` real **NO existe** en tu PC, **solo lo crearás en EC2** con `nano .env` 🚀
