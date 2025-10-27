# 🚀 Script de Deploy Rápido para EC2
# Este script automatiza el proceso de deployment en AWS EC2

#!/bin/bash

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  CarroIoT - Deployment Script para EC2${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 no está instalado${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 está instalado${NC}"
        return 0
    fi
}

# Función para imprimir paso
print_step() {
    echo ""
    echo -e "${YELLOW}▶ $1${NC}"
    echo "-----------------------------------"
}

# 1. Verificar requisitos
print_step "Paso 1: Verificando requisitos del sistema"
check_command python3
check_command pip3
check_command git
check_command mysql

# 2. Clonar o actualizar repositorio
print_step "Paso 2: Obteniendo código desde GitHub"

REPO_URL="https://github.com/TU_USUARIO/CarroIoT.git"
PROJECT_DIR="$HOME/CarroIoT"

if [ -d "$PROJECT_DIR" ]; then
    echo "Directorio existe, actualizando..."
    cd "$PROJECT_DIR"
    git pull origin main
else
    echo "Clonando repositorio..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
fi

cd "$PROJECT_DIR/backend-api"

# 3. Crear virtual environment
print_step "Paso 3: Configurando entorno virtual Python"

if [ ! -d "venv" ]; then
    echo "Creando virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment ya existe"
fi

# Activar venv
source venv/bin/activate

# 4. Instalar dependencias
print_step "Paso 4: Instalando dependencias Python"
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Dependencias instaladas correctamente${NC}"

# 5. Verificar archivo .env
print_step "Paso 5: Verificando configuración"

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
    echo "Copiando .env.example a .env..."
    cp .env.example .env
    echo ""
    echo -e "${RED}⚠️  IMPORTANTE: Debes editar .env con tus credenciales de Aurora RDS${NC}"
    echo "Ejecuta: nano .env"
    echo ""
    read -p "¿Quieres editar .env ahora? (y/n): " edit_env
    if [ "$edit_env" = "y" ]; then
        nano .env
    fi
else
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
fi

# 6. Verificar conexión a Aurora
print_step "Paso 6: Verificando conexión a Aurora RDS"

# Cargar variables de .env
export $(cat .env | grep -v '^#' | xargs)

echo "Intentando conectar a: $DB_HOST"
echo "Usuario: $DB_USER"
echo "Base de datos: $DB_NAME"
echo ""

read -p "¿Deseas probar la conexión a Aurora? (y/n): " test_connection
if [ "$test_connection" = "y" ]; then
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT 1 as connection_test;"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Conexión a Aurora exitosa${NC}"
    else
        echo -e "${RED}❌ Error al conectar a Aurora. Verifica tus credenciales en .env${NC}"
        exit 1
    fi
fi

# 7. Inicializar base de datos (solo primera vez)
print_step "Paso 7: Inicializar base de datos (SOLO PRIMERA VEZ)"

read -p "¿Es la primera vez que despliegas? ¿Deseas ejecutar init_database.sql? (y/n): " init_db
if [ "$init_db" = "y" ]; then
    echo "Ejecutando init_database.sql..."
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" < init_database.sql
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Base de datos inicializada correctamente${NC}"
    else
        echo -e "${RED}❌ Error al inicializar base de datos${NC}"
    fi
else
    echo "Omitiendo inicialización de base de datos..."
fi

# 8. Probar aplicación
print_step "Paso 8: Probando aplicación"

echo "Iniciando servidor en modo de prueba (presiona Ctrl+C para detener)..."
echo ""
python src/app.py &
APP_PID=$!

sleep 5

# Test de health check
curl -s http://localhost:5500/health | jq . || echo "Respuesta recibida"

echo ""
echo "Presiona Enter para detener el servidor de prueba..."
read
kill $APP_PID

# 9. Configurar servicio systemd
print_step "Paso 9: Configurar servicio systemd"

read -p "¿Deseas configurar el servicio systemd para auto-inicio? (y/n): " setup_systemd
if [ "$setup_systemd" = "y" ]; then
    sudo bash -c "cat > /etc/systemd/system/carrito-iot.service << EOF
[Unit]
Description=CarroIoT Backend API
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/backend-api
Environment=\"PATH=$PROJECT_DIR/backend-api/venv/bin\"
ExecStart=$PROJECT_DIR/backend-api/venv/bin/python src/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

    sudo systemctl daemon-reload
    sudo systemctl enable carrito-iot
    sudo systemctl start carrito-iot
    
    echo -e "${GREEN}✅ Servicio configurado y iniciado${NC}"
    echo "Ver estado: sudo systemctl status carrito-iot"
    echo "Ver logs: sudo journalctl -u carrito-iot -f"
else
    echo "Servicio systemd no configurado. Deberás iniciar manualmente con: python src/app.py"
fi

# 10. Verificar Security Group
print_step "Paso 10: Recordatorio de Security Group"

echo -e "${YELLOW}⚠️  Asegúrate de que tu Security Group de EC2 permita:${NC}"
echo "   - Puerto 5500 (TCP) desde 0.0.0.0/0 (o tu IP específica)"
echo "   - Puerto 22 (SSH) desde tu IP"
echo ""
echo "AWS Console → EC2 → Security Groups → Tu SG → Inbound Rules"

# 11. Resumen final
print_step "✅ Deploy completado"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Resumen de Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "📦 Proyecto: $PROJECT_DIR"
echo "🐍 Python Virtual Env: $PROJECT_DIR/backend-api/venv"
echo "🗄️  Base de datos: $DB_HOST"
echo "🌐 Servidor: http://$(curl -s ifconfig.me):5500"
echo ""
echo -e "${YELLOW}Comandos útiles:${NC}"
echo "  Reiniciar:  sudo systemctl restart carrito-iot"
echo "  Detener:    sudo systemctl stop carrito-iot"
echo "  Ver logs:   sudo journalctl -u carrito-iot -f"
echo "  Actualizar: cd $PROJECT_DIR && git pull && sudo systemctl restart carrito-iot"
echo ""
echo -e "${GREEN}¡Deployment exitoso! 🚀${NC}"
echo ""

# Mostrar IP pública
PUBLIC_IP=$(curl -s ifconfig.me)
echo -e "${YELLOW}Tu IP pública es: ${GREEN}$PUBLIC_IP${NC}"
echo "Actualiza frontend-web/js/config.js con esta IP antes de subir a GitHub Pages"
echo ""
