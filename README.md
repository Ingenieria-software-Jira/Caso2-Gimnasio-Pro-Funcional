# 🏋️ Gimnasio Pro Funcional - Panel de Usuario con Historial de Reservas

Sistema web completo para la gestión de reservas de un gimnasio, con integración de pagos mediante Webpay Plus (Transbank), sistema de notificaciones por email y SMS, y panel de administración.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Base de Datos](#-base-de-datos)
- [Ejecución](#-ejecución)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [API Endpoints](#-api-endpoints)
- [Notas Importantes](#-notas-importantes)
- [Solución de Problemas](#-solución-de-problemas)

## ✨ Características

- 🔐 Sistema de autenticación y roles (Cliente, Admin, Entrenador)
- 📅 Gestión de reservas de clases (Cardio y Fuerza)
- 💳 Integración con Webpay Plus para pagos
- 📧 Notificaciones por email (Gmail SMTP)
- 📱 Notificaciones por SMS (Twilio)
- 👥 Gestión de entrenadores
- 📊 Panel de administración
- 📜 Historial de reservas por usuario

## 🔧 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.8 o superior**
- **MySQL 5.7 o superior** (o MariaDB 10.3+)
- **pip** (gestor de paquetes de Python)
- **Git** (opcional, para clonar el repositorio)

### Verificar instalaciones

```bash
# Verificar Python
python --version
# o
python3 --version

# Verificar pip
pip --version
# o
pip3 --version

# Verificar MySQL
mysql --version
```

## 📦 Instalación

### 1. Clonar o descargar el proyecto

Si tienes el proyecto en Git:
```bash
git clone <url-del-repositorio>
cd Caso2-Gimnasio-Pro-Funcional-IESC2-23-Panel-de-usuario-con-historial-de-reservas
```

Si tienes el proyecto como carpeta, simplemente navega a ella:
```bash
cd Caso2-Gimnasio-Pro-Funcional-IESC2-23-Panel-de-usuario-con-historial-de-reservas
```

### 2. Crear un entorno virtual (Recomendado)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si tienes problemas con `mysqlclient`, puedes intentar:

**Windows:**
- Descargar el instalador desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
- O usar: `pip install mysqlclient --only-binary :all:`

**Linux:**
```bash
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install mysqlclient
```

**Mac:**
```bash
brew install mysql
pip install mysqlclient
```

### 4. Instalar dependencias adicionales

El proyecto también requiere el SDK de Transbank:
```bash
pip install transbank-sdk
```

## ⚙️ Configuración

### 1. Configurar la Base de Datos MySQL

Edita el archivo `config.py` con tus credenciales de MySQL:

```python
# config.py
MYSQL_HOST = 'localhost'  # Cambia si tu MySQL está en otro servidor
MYSQL_USER = 'root'       # Tu usuario de MySQL
MYSQL_PASSWORD = 'tu_contraseña'  # Tu contraseña de MySQL
MYSQL_DB = 'gimnasio_db'  # Nombre de la base de datos
MYSQL_PORT = 3306         # Puerto de MySQL (por defecto 3306)
```

### 2. Configurar Webpay (Transbank)

Edita el archivo `webpay_config.py`:

**Para desarrollo/pruebas (INTEGRATION):**
```python
WEBPAY_ENVIRONMENT = "INTEGRATION"
WEBPAY_COMMERCE_CODE = "597055555532"  # Código de pruebas
WEBPAY_API_KEY = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"  # API Key de pruebas
WEBPAY_RETURN_URL = "http://localhost:5000/api/webpay/confirmar"
PRECIO_RESERVA = 1  # Monto en CLP para pruebas
```

**Para producción:**
```python
WEBPAY_ENVIRONMENT = "PRODUCTION"
WEBPAY_COMMERCE_CODE = "tu_codigo_comercio_real"
WEBPAY_API_KEY = "tu_api_key_real"
WEBPAY_RETURN_URL = "https://tu-dominio.com/api/webpay/confirmar"
PRECIO_RESERVA = 10000  # Monto real en CLP
```

> ⚠️ **IMPORTANTE:** Las credenciales de producción deben obtenerse desde el panel de Transbank.

### 3. Configurar Notificaciones

Edita el archivo `notificaciones_config.py`:

**Gmail SMTP:**
```python
GMAIL_EMAIL = 'tu_email@gmail.com'
GMAIL_PASSWORD = 'tu_app_password'  # Contraseña de aplicación de Gmail
GMAIL_SMTP_SERVER = 'smtp.gmail.com'
GMAIL_SMTP_PORT = 587
```

> 📝 **Nota:** Para usar Gmail, necesitas generar una "Contraseña de aplicación" desde tu cuenta de Google:
> 1. Ve a tu cuenta de Google → Seguridad
> 2. Activa la verificación en 2 pasos
> 3. Genera una "Contraseña de aplicación" para "Correo"

**Twilio SMS:**
```python
TWILIO_ACCOUNT_SID = 'tu_account_sid'
TWILIO_AUTH_TOKEN = 'tu_auth_token'
TWILIO_PHONE_NUMBER = '+1234567890'  # Número de Twilio
VERIFIED_PHONE_NUMBERS = ['+56912345678']  # Números verificados (cuenta trial)
```

> 📝 **Nota:** En cuentas de prueba de Twilio, solo puedes enviar SMS a números verificados.

**Habilitar/Deshabilitar notificaciones:**
```python
NOTIFICATIONS_ENABLED = True
SMS_ENABLED = True
EMAIL_ENABLED = True
```

## 🗄️ Base de Datos

### 1. Crear la base de datos

Abre MySQL y ejecuta el script SQL:

```bash
mysql -u root -p < database.sql
```

O desde el cliente MySQL:
```sql
mysql -u root -p
source database.sql
```

O copia y pega el contenido de `database.sql` en tu cliente MySQL (phpMyAdmin, MySQL Workbench, etc.).

### 2. Verificar la creación

```sql
USE gimnasio_db;
SHOW TABLES;
```

Deberías ver las tablas:
- `usuarios`
- `entrenadores`
- `reservas`
- `bloques`
- `pagos`

## 🚀 Ejecución

### 1. Activar el entorno virtual (si lo usas)

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Ejecutar el servidor

```bash
python backend.py
```

O si usas Python 3 explícitamente:
```bash
python3 backend.py
```

### 3. Acceder a la aplicación

Abre tu navegador y ve a:
```
http://localhost:5000
```

El servidor Flask estará corriendo en el puerto 5000 por defecto.

## 📁 Estructura del Proyecto

```
Caso2-Gimnasio-Pro-Funcional-IESC2-23-Panel-de-usuario-con-historial-de-reservas/
│
├── backend.py                 # Servidor Flask principal
├── config.py                  # Configuración de MySQL
├── webpay_config.py           # Configuración de Webpay
├── notificaciones_config.py   # Configuración de notificaciones
├── notificaciones.py          # Lógica de notificaciones
├── db_helpers.py             # Funciones auxiliares de BD
├── app_webpay.py             # (Archivo alternativo de Webpay)
│
├── index.html                # Página principal (frontend)
├── confirmar-reserva.html    # Página de confirmación
├── pago-exitoso.html         # Página de pago exitoso
├── pago-fallido.html         # Página de pago fallido
├── script_integrado.js       # JavaScript del frontend
├── style.css                 # Estilos CSS
│
├── database.sql              # Script de creación de BD
├── requirements.txt          # Dependencias de Python
│
├── API_DOCUMENTATION.md      # Documentación de la API
├── README_NOTIFICACIONES.md  # Documentación de notificaciones
├── SPRINT1_REFACTORIZACION_COMPLETA.md  # Documentación técnica
│
└── README.md                 # Este archivo
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 3.0.0** - Framework web de Python
- **Flask-CORS 4.0.0** - Manejo de CORS
- **PyMySQL** - Conector MySQL para Python
- **python-dotenv 1.0.0** - Manejo de variables de entorno
- **Transbank SDK** - Integración con Webpay Plus

### Base de Datos
- **MySQL 5.7+** - Sistema de gestión de bases de datos

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos
- **JavaScript (Vanilla)** - Lógica del cliente

### Servicios Externos
- **Transbank Webpay Plus** - Pasarela de pagos
- **Gmail SMTP** - Envío de emails
- **Twilio** - Envío de SMS

## 🔌 API Endpoints

### Autenticación
- `POST /api/login` - Iniciar sesión
- `POST /api/registro` - Registrar nuevo usuario

### Reservas
- `GET /api/reservas` - Obtener reservas del usuario
- `POST /api/reservas` - Crear nueva reserva
- `DELETE /api/reservas/<id>` - Cancelar reserva

### Webpay
- `POST /api/webpay/crear` - Crear transacción de pago
- `POST /api/webpay/confirmar` - Confirmar pago

### Administración
- `GET /api/admin/reservas` - Ver todas las reservas (admin)
- `GET /api/admin/bloques` - Gestionar bloques (admin)
- `POST /api/admin/bloques` - Crear bloque (admin)

Para más detalles, consulta `API_DOCUMENTATION.md`.

## ⚠️ Notas Importantes

### Seguridad

1. **Credenciales sensibles:** Los archivos `config.py`, `webpay_config.py` y `notificaciones_config.py` contienen credenciales. **NO subas estos archivos con credenciales reales a repositorios públicos.**

2. **Variables de entorno:** Considera usar variables de entorno o un archivo `.env` para credenciales:
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
   ```

3. **Producción:** Antes de desplegar a producción:
   - Cambia `DEBUG = False` en `config.py`
   - Usa credenciales de producción de Transbank
   - Configura HTTPS
   - Usa un servidor WSGI (Gunicorn, uWSGI)

### Base de Datos

- El script `database.sql` incluye datos de ejemplo. Elimínalos en producción.
- Asegúrate de hacer backups regulares de la base de datos.

### Webpay

- En modo INTEGRATION, puedes usar tarjetas de prueba de Transbank.
- Las transacciones de prueba no realizan cargos reales.

## 🔍 Solución de Problemas

### Error: "No module named 'pymysql'"
```bash
pip install pymysql
```

### Error: "Can't connect to MySQL server"
- Verifica que MySQL esté corriendo
- Revisa las credenciales en `config.py`
- Verifica que el puerto 3306 esté abierto

### Error: "ModuleNotFoundError: No module named 'transbank'"
```bash
pip install transbank-sdk
```

### Error al instalar mysqlclient
- **Windows:** Descarga el wheel desde https://www.lfd.uci.edu/~gohlke/pythonlibs/
- **Linux:** Instala las dependencias del sistema: `sudo apt-get install python3-dev default-libmysqlclient-dev`
- **Mac:** `brew install mysql`

### El servidor no inicia
- Verifica que el puerto 5000 no esté en uso
- Cambia el puerto en `config.py` si es necesario
- Revisa los logs de error en la consola

### Problemas con notificaciones
- **Email:** Verifica que uses una "Contraseña de aplicación" de Gmail, no tu contraseña normal
- **SMS:** En cuentas trial de Twilio, solo puedes enviar a números verificados

## 📝 Licencia

Este proyecto fue desarrollado como parte de un caso de estudio académico.

## 👥 Contribuidores

- Equipo de desarrollo IESC2-23

## 📞 Soporte

Para problemas o preguntas, revisa la documentación en:
- `API_DOCUMENTATION.md`
- `README_NOTIFICACIONES.md`

---

**¡Listo para usar!** 🎉

Si encuentras algún problema, revisa la sección de [Solución de Problemas](#-solución-de-problemas) o consulta la documentación adicional del proyecto.
