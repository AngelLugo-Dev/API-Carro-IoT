# Script para probar la conexión a MySQL RDS desde Windows
# Ejecutar: powershell -ExecutionPolicy Bypass .\test-mysql-connection.ps1

Write-Host "🔍 Probando conexión a MySQL RDS..." -ForegroundColor Cyan
Write-Host ""

$dbHost = "instance-iot.cjsq62eqm24v.us-east-1.rds.amazonaws.com"
$dbPort = 3306
$dbUser = "admin"
$dbPassword = "Admin12345#!"
$dbName = "iot_car_control"

Write-Host "📋 Configuración:" -ForegroundColor Yellow
Write-Host "Host: $dbHost"
Write-Host "Port: $dbPort"
Write-Host "User: $dbUser"
Write-Host "Database: $dbName"
Write-Host ""

# Probar conexión TCP al puerto 3306
Write-Host "🔌 1. Probando conectividad TCP al puerto 3306..." -ForegroundColor Yellow
try {
    $tcpTest = Test-NetConnection -ComputerName $dbHost -Port $dbPort -WarningAction SilentlyContinue
    if ($tcpTest.TcpTestSucceeded) {
        Write-Host "✅ Puerto 3306 accesible" -ForegroundColor Green
    } else {
        Write-Host "❌ No se puede conectar al puerto 3306" -ForegroundColor Red
        Write-Host "Verifica que el Security Group de RDS permita conexiones desde tu IP" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error al probar conexión TCP: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🐍 2. Probando conexión con Python y PyMySQL..." -ForegroundColor Yellow

# Crear script Python temporal
$pythonScript = @"
import sys
try:
    import pymysql
    
    print("Conectando a MySQL RDS...")
    connection = pymysql.connect(
        host='$dbHost',
        port=$dbPort,
        user='$dbUser',
        password='$dbPassword',
        database='$dbName',
        connect_timeout=10
    )
    
    print("✅ Conexión exitosa!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE(), VERSION();")
        result = cursor.fetchone()
        print(f"📊 Base de datos: {result[0]}")
        print(f"🔧 Versión MySQL: {result[1]}")
        
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print(f"📋 Tablas encontradas: {len(tables)}")
        if tables:
            print("Tablas:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("⚠️  No hay tablas creadas aún")
    
    connection.close()
    print("")
    print("✅ MySQL RDS configurado correctamente!")
    
except ImportError:
    print("❌ PyMySQL no está instalado")
    print("Instala con: pip install PyMySQL")
    sys.exit(1)
except pymysql.err.OperationalError as e:
    print(f"❌ Error de conexión: {e}")
    print("")
    print("Posibles causas:")
    print("1. Security Group de RDS no permite tu IP")
    print("2. Credenciales incorrectas")
    print("3. Base de datos no existe")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
"@

$pythonScript | Out-File -FilePath "temp_test_mysql.py" -Encoding UTF8

try {
    python temp_test_mysql.py
    $exitCode = $LASTEXITCODE
} finally {
    Remove-Item "temp_test_mysql.py" -ErrorAction SilentlyContinue
}

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "🎉 ¡Conexión a MySQL RDS exitosa!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
    Write-Host "1. El archivo .env ya está creado con las credenciales" -ForegroundColor White
    Write-Host "2. En EC2, copia el archivo .env al servidor" -ForegroundColor White
    Write-Host "3. Reinicia el servidor API en EC2" -ForegroundColor White
} else {
    Write-Host "❌ Hubo problemas con la conexión" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Soluciones:" -ForegroundColor Yellow
    Write-Host "1. Ve a AWS Console → RDS → instance-iot → Security Groups" -ForegroundColor White
    Write-Host "2. Edita las reglas de entrada (Inbound rules)" -ForegroundColor White
    Write-Host "3. Agrega tu IP o 0.0.0.0/0 para permitir conexiones" -ForegroundColor White
}
