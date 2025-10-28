#!/bin/bash
# Script para verificar y solucionar problemas de conexión MySQL
# Ejecutar en EC2: bash check-mysql.sh

echo "🔍 Verificando conexión a MySQL RDS..."
echo ""

# Variables (ajusta según tu configuración)
DB_HOST="instance-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com"
DB_USER="admin"
DB_NAME="iot_car_control"
DB_PORT=3306

echo "📋 Configuración:"
echo "Host: $DB_HOST"
echo "User: $DB_USER"
echo "Database: $DB_NAME"
echo "Port: $DB_PORT"
echo ""

# Verificar si mysql client está instalado
if ! command -v mysql &> /dev/null; then
    echo "⚠️  MySQL client no está instalado"
    echo "Instalando..."
    sudo yum install mysql -y || sudo apt-get install mysql-client -y
fi

# Leer contraseña del archivo .env si existe
if [ -f .env ]; then
    echo "✅ Archivo .env encontrado"
    DB_PASSWORD=$(grep IOT_DB_PASSWORD .env | cut -d '=' -f2)
    
    if [ -z "$DB_PASSWORD" ]; then
        echo "❌ Contraseña vacía en .env"
        echo "Por favor edita .env y agrega: IOT_DB_PASSWORD=tu_contraseña"
        exit 1
    fi
else
    echo "❌ Archivo .env no encontrado"
    echo ""
    echo "Creando .env de ejemplo..."
    cat > .env << EOF
# Contraseña de MySQL RDS
IOT_DB_PASSWORD=TU_CONTRASEÑA_AQUI
EOF
    echo "✅ Archivo .env creado"
    echo "⚠️  Por favor edita .env y agrega tu contraseña real"
    exit 1
fi

echo ""
echo "🔌 Probando conexión a MySQL..."
mysql -h $DB_HOST -u $DB_USER -p"$DB_PASSWORD" -P $DB_PORT -e "SELECT 1 as test;" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡Conexión exitosa!"
    echo ""
    echo "Verificando base de datos '$DB_NAME'..."
    mysql -h $DB_HOST -u $DB_USER -p"$DB_PASSWORD" -P $DB_PORT -e "SHOW DATABASES LIKE '$DB_NAME';"
    
    echo ""
    echo "📊 Tablas en la base de datos:"
    mysql -h $DB_HOST -u $DB_USER -p"$DB_PASSWORD" -P $DB_PORT $DB_NAME -e "SHOW TABLES;"
else
    echo ""
    echo "❌ Error de conexión"
    echo ""
    echo "Posibles causas:"
    echo "1. Contraseña incorrecta en .env"
    echo "2. Security Group de RDS no permite conexión desde EC2"
    echo "3. RDS no está en ejecución"
    echo ""
    echo "🔧 Soluciones:"
    echo "1. Verifica la contraseña en .env"
    echo "2. En AWS Console → RDS → Security Groups"
    echo "   - Asegúrate que permita conexión desde el Security Group de EC2"
    echo "   - O permite desde la IP de EC2"
fi

echo ""
echo "🔄 Para reiniciar el servidor API después de arreglar:"
echo "pkill -f uvicorn"
echo "nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 5500 > api.log 2>&1 &"
