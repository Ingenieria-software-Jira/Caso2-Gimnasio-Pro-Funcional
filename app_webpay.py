"""
Backend con integración de Webpay Plus
Gimnasio Pro Funcional
"""
from flask import Flask, request, jsonify, redirect, send_from_directory
from flask_cors import CORS
import pymysql
from datetime import datetime
import os
import config
import webpay_config
import notificaciones

# Importar SDK de Transbank
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.integration_type import IntegrationType

app = Flask(__name__, static_folder='.')
CORS(app)

# Crear instancia de Transaction según el ambiente
if webpay_config.WEBPAY_ENVIRONMENT == 'INTEGRATION':
    # Ambiente de integración con credenciales de prueba
    tx_handler = Transaction.build_for_integration(
        "597055555532",
        "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
    )
else:
    # Ambiente de producción con tus credenciales reales
    tx_handler = Transaction.build_for_production(
        webpay_config.WEBPAY_COMMERCE_CODE,
        webpay_config.WEBPAY_API_KEY
    )

# Configuración de MySQL usando PyMySQL
def get_db_connection():
    return pymysql.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB,
        cursorclass=pymysql.cursors.DictCursor
    )

# Función para obtener el precio desde la base de datos
def obtener_precio_reserva():
    """Obtiene el precio de reserva desde la base de datos"""
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE nombre = 'precio_reserva'")
        resultado = cur.fetchone()
        cur.close()
        connection.close()
        
        if resultado:
            return int(resultado['valor'])
        else:
            # Si no existe en la BD, usar el valor por defecto de webpay_config
            return webpay_config.PRECIO_RESERVA
    except Exception as e:
        print(f"Error al obtener precio desde BD: {e}")
        # En caso de error, usar el valor por defecto
        return webpay_config.PRECIO_RESERVA

# ==================== USUARIOS ====================
@app.route('/api/registro', methods=['POST'])
def registro():
    """Registro de nuevos usuarios"""
    try:
        data = request.json
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        fecha_nacimiento = data.get('fecha_nacimiento')
        email = data.get('email')
        telefono = data.get('telefono')
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')
        
        # Validaciones
        if not all([nombre, apellido, email, telefono, username, password, role]):
            return jsonify({'error': 'Todos los campos son obligatorios'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verificar si el username ya existe
        cur.execute("SELECT * FROM usuarios WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            connection.close()
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
        
        # Verificar si el email ya existe (solo si no es NULL)
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND email IS NOT NULL", (email,))
        if cur.fetchone():
            cur.close()
            connection.close()
            return jsonify({'error': 'El email ya está registrado'}), 400
        
        # Insertar nuevo usuario
        cur.execute("""
            INSERT INTO usuarios (username, nombre, apellido, email, password, telefono, fecha_nacimiento, rol)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (username, nombre, apellido, email, password, telefono, fecha_nacimiento, role))
        
        connection.commit()
        user_id = cur.lastrowid
        
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'Usuario registrado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        
        if not email or not password or not role:
            return jsonify({'error': 'Email, contraseña y rol son requeridos'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Buscar usuario con email, password y rol
        cur.execute("SELECT * FROM usuarios WHERE email = %s AND password = %s AND rol = %s", 
                   (email, password, role))
        user = cur.fetchone()
        
        cur.close()
        connection.close()
        
        if not user:
            return jsonify({'error': 'Email, contraseña o rol incorrectos'}), 401
        
        return jsonify({
            'success': True,
            'user_id': user['id'],
            'username': user.get('username', ''),
            'email': email,
            'role': role,
            'nombre': user.get('nombre', ''),
            'apellido': user.get('apellido', '')
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ADMINISTRADOR ====================
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Login para administradores"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT * FROM administradores WHERE username = %s AND password = %s", (username, password))
        admin = cur.fetchone()
        
        cur.close()
        connection.close()
        
        if not admin:
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        return jsonify({
            'success': True,
            'admin_id': admin['id'],
            'username': admin['username'],
            'nombre': admin['nombre'],
            'role': 'admin'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/configuracion/<nombre>', methods=['GET'])
def obtener_configuracion(nombre):
    """Obtener valor de configuración"""
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT valor FROM configuracion WHERE nombre = %s", (nombre,))
        config = cur.fetchone()
        
        cur.close()
        connection.close()
        
        if not config:
            return jsonify({'error': 'Configuración no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'nombre': nombre,
            'valor': config['valor']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/configuracion/<nombre>', methods=['PUT'])
def actualizar_configuracion(nombre):
    """Actualizar valor de configuración"""
    try:
        data = request.json
        valor = data.get('valor')
        
        if valor is None:
            return jsonify({'error': 'Valor es requerido'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Actualizar o insertar
        cur.execute("""
            INSERT INTO configuracion (nombre, valor, descripcion)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE valor = %s, fecha_modificacion = CURRENT_TIMESTAMP
        """, (nombre, str(valor), f'Configuración de {nombre}', str(valor)))
        
        connection.commit()
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Configuración actualizada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/entrenadores', methods=['POST'])
def crear_entrenador():
    """Crear nuevo entrenador (solo admin)"""
    try:
        data = request.json
        nombre = data.get('nombre')
        especialidad = data.get('especialidad', '')
        
        if not nombre:
            return jsonify({'error': 'Nombre es requerido'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verificar si ya existe
        cur.execute("SELECT * FROM entrenadores WHERE nombre = %s", (nombre,))
        existe = cur.fetchone()
        
        if existe:
            cur.close()
            connection.close()
            return jsonify({'error': 'El entrenador ya existe'}), 400
        
        cur.execute("""
            INSERT INTO entrenadores (nombre, especialidad)
            VALUES (%s, %s)
        """, (nombre, especialidad))
        
        connection.commit()
        entrenador_id = cur.lastrowid
        
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'entrenador_id': entrenador_id,
            'message': 'Entrenador creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/cupos', methods=['POST'])
def crear_cupo():
    """Crear nuevo cupo/slot (solo admin)"""
    try:
        data = request.json
        fecha = data.get('fecha')
        hora = data.get('hora')
        entrenador_nombre = data.get('entrenador_nombre')
        actividad = data.get('actividad')
        capacidad_maxima = data.get('capacidad_maxima', 10)
        
        if not all([fecha, hora, entrenador_nombre, actividad]):
            return jsonify({'error': 'Todos los campos son requeridos'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Verificar que el entrenador existe
        cur.execute("SELECT * FROM entrenadores WHERE nombre = %s", (entrenador_nombre,))
        entrenador = cur.fetchone()
        
        if not entrenador:
            cur.close()
            connection.close()
            return jsonify({'error': 'Entrenador no encontrado'}), 404
        
        # Crear el cupo
        cur.execute("""
            INSERT INTO cupos (fecha, hora, entrenador_nombre, actividad, capacidad_maxima, creado_por)
            VALUES (%s, %s, %s, %s, %s, 'admin')
        """, (fecha, hora, entrenador_nombre, actividad, capacidad_maxima))
        
        connection.commit()
        cupo_id = cur.lastrowid
        
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'cupo_id': cupo_id,
            'message': 'Cupo creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cupos/disponibles', methods=['GET'])
def obtener_cupos_disponibles():
    """Obtener cupos disponibles a futuro"""
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Obtener solo cupos futuros y disponibles
        cur.execute("""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM reservas r 
                    WHERE r.fecha = c.fecha AND r.hora = c.hora 
                    AND r.entrenador_id = (SELECT id FROM entrenadores WHERE nombre = c.entrenador_nombre)
                    AND r.estado IN ('confirmada', 'pendiente_pago')) as reservas_actuales
            FROM cupos c
            WHERE c.fecha >= CURDATE() AND c.disponible = TRUE
            ORDER BY c.fecha, c.hora
        """)
        
        cupos = cur.fetchall()
        
        # Convertir time y date a string
        for cupo in cupos:
            if 'hora' in cupo and cupo['hora']:
                cupo['hora'] = str(cupo['hora'])
            if 'fecha' in cupo and cupo['fecha']:
                cupo['fecha'] = str(cupo['fecha'])
            if 'fecha_creacion' in cupo and cupo['fecha_creacion']:
                cupo['fecha_creacion'] = str(cupo['fecha_creacion'])
            # Calcular disponibilidad
            cupo['disponible'] = cupo['reservas_actuales'] < cupo['capacidad_maxima']
            cupo['plazas_disponibles'] = cupo['capacidad_maxima'] - cupo['reservas_actuales']
        
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'cupos': cupos
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:user_id>', methods=['GET', 'PUT'])
def gestionar_usuario(user_id):
    """Obtener o actualizar información del usuario"""
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        if request.method == 'GET':
            cur.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            usuario = cur.fetchone()
            
            if not usuario:
                cur.close()
                connection.close()
                return jsonify({'error': 'Usuario no encontrado'}), 404
            
            # Convertir fecha a string si existe
            if 'fecha_nacimiento' in usuario and usuario['fecha_nacimiento']:
                usuario['fecha_nacimiento'] = str(usuario['fecha_nacimiento'])
            
            cur.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'usuario': usuario
            }), 200
        
        elif request.method == 'PUT':
            data = request.json
            
            # Campos que se pueden actualizar
            campos_actualizables = ['email', 'telefono', 'direccion', 'fecha_nacimiento', 
                                   'peso', 'altura', 'objetivo']
            
            # Construir query dinámicamente
            updates = []
            valores = []
            
            for campo in campos_actualizables:
                if campo in data:
                    updates.append(f"{campo} = %s")
                    valores.append(data[campo])
            
            if not updates:
                cur.close()
                connection.close()
                return jsonify({'error': 'No hay campos para actualizar'}), 400
            
            valores.append(user_id)
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
            
            cur.execute(query, tuple(valores))
            connection.commit()
            
            cur.close()
            connection.close()
            
            return jsonify({
                'success': True,
                'message': 'Usuario actualizado exitosamente'
            }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== WEBPAY - CREAR TRANSACCIÓN ====================
@app.route('/api/webpay/crear', methods=['POST'])
def crear_transaccion_webpay():
    """
    Crea una transacción en Webpay y devuelve URL y token para redirigir al usuario
    """
    try:
        data = request.json
        
        # Verificar si viene con bloque_id (nuevo método) o con datos directos (método antiguo)
        bloque_id = data.get('bloque_id')
        user_id = data.get('usuario_id') or data.get('user_id')
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Caso especial: Sin entrenador (reserva libre)
        if bloque_id == 'sin_entrenador':
            actividad = data.get('actividad')
            fecha = data.get('fecha')
            hora = data.get('hora')
            
            # Validar que vengan los datos necesarios desde sessionStorage
            if not actividad or not fecha or not hora:
                cur.close()
                connection.close()
                return jsonify({'error': 'Faltan datos para la reserva sin entrenador'}), 400
            
            # Formatear hora si es necesario (agregar :00 si solo tiene HH:MM)
            if len(hora.split(':')) == 2:
                hora = hora + ':00'
            
            entrenador_id = None  # Sin entrenador asignado
            entrenador_nombre = 'Sin entrenador'
        
        # Si viene bloque_id normal, obtener los datos del bloque
        elif bloque_id:
            cur.execute("""
                SELECT b.*, e.nombre as nombre_entrenador, e.id as entrenador_id
                FROM bloques b
                LEFT JOIN entrenadores e ON b.entrenador_id = e.id
                WHERE b.id = %s
            """, (bloque_id,))
            bloque = cur.fetchone()
            
            if not bloque:
                cur.close()
                connection.close()
                return jsonify({'error': 'Bloque no encontrado'}), 404
            
            actividad = bloque['actividad']
            fecha = str(bloque['fecha'])
            hora = str(bloque['hora'])
            entrenador_id = bloque['entrenador_id']
            entrenador_nombre = bloque['nombre_entrenador']
        else:
            # Método antiguo: recibir datos directamente
            actividad = data.get('actividad')
            fecha = data.get('fecha')
            hora = data.get('hora')
            entrenador_nombre = data.get('entrenador')
            
            # Obtener ID del entrenador
            cur.execute("SELECT id FROM entrenadores WHERE nombre = %s", (entrenador_nombre,))
            entrenador = cur.fetchone()
            
            if not entrenador:
                cur.close()
                connection.close()
                return jsonify({'error': 'Entrenador no encontrado'}), 404
            
            entrenador_id = entrenador['id']
        
        # Generar orden de compra única
        buy_order = f"GYM-{user_id}-{int(datetime.now().timestamp())}"
        session_id = str(user_id)
        amount = obtener_precio_reserva()  # Obtener precio desde la BD
        return_url = webpay_config.WEBPAY_RETURN_URL
        
        # Crear reserva temporal con estado pendiente
        cur.execute("""
            INSERT INTO reservas (usuario_id, actividad, fecha, hora, entrenador_id, estado, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, 'pendiente_pago', NOW())
        """, (user_id, actividad, fecha, hora, entrenador_id))
        
        connection.commit()
        reserva_id = cur.lastrowid
        
        # Guardar relación entre buy_order y reserva_id
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transacciones_webpay (
                id INT AUTO_INCREMENT PRIMARY KEY,
                buy_order VARCHAR(100) UNIQUE NOT NULL,
                reserva_id INT NOT NULL,
                token VARCHAR(100),
                amount INT NOT NULL,
                estado VARCHAR(50) DEFAULT 'iniciada',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reserva_id) REFERENCES reservas(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        connection.commit()
        
        cur.execute("""
            INSERT INTO transacciones_webpay (buy_order, reserva_id, amount)
            VALUES (%s, %s, %s)
        """, (buy_order, reserva_id, amount))
        
        connection.commit()
        cur.close()
        connection.close()
        
        # Crear transacción en Webpay
        response = tx_handler.create(buy_order, session_id, amount, return_url)
        
        # Actualizar token en la BD
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("""
            UPDATE transacciones_webpay 
            SET token = %s 
            WHERE buy_order = %s
        """, (response['token'], buy_order))
        connection.commit()
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'url': response['url'],
            'token': response['token'],
            'buy_order': buy_order,
            'amount': amount
        }), 200
        
    except Exception as e:
        print(f"Error creando transacción Webpay: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== WEBPAY - CONFIRMAR TRANSACCIÓN ====================
@app.route('/api/webpay/confirmar', methods=['POST', 'GET'])
def confirmar_transaccion_webpay():
    """
    Endpoint que recibe la confirmación desde Webpay
    """
    try:
        # Webpay puede enviar por GET o POST
        if request.method == 'GET':
            token_ws = request.args.get('token_ws')
            # Si el usuario canceló o hubo error, Transbank envía TBK_TOKEN
            tbk_token = request.args.get('TBK_TOKEN')
            tbk_orden = request.args.get('TBK_ORDEN_COMPRA')
        else:
            token_ws = request.form.get('token_ws')
            tbk_token = request.form.get('TBK_TOKEN')
            tbk_orden = request.form.get('TBK_ORDEN_COMPRA')
        
        # Si hay TBK_TOKEN, significa que el pago fue cancelado/rechazado
        if tbk_token and tbk_orden:
            # Buscar la transacción por orden de compra
            connection = get_db_connection()
            cur = connection.cursor()
            
            cur.execute("""
                SELECT * FROM transacciones_webpay 
                WHERE buy_order = %s
            """, (tbk_orden,))
            
            transaccion = cur.fetchone()
            
            if transaccion:
                # Marcar como rechazada
                cur.execute("""
                    UPDATE reservas 
                    SET estado = 'cancelada' 
                    WHERE id = %s
                """, (transaccion['reserva_id'],))
                
                cur.execute("""
                    UPDATE transacciones_webpay 
                    SET estado = 'rechazada' 
                    WHERE id = %s
                """, (transaccion['id'],))
                
                connection.commit()
            
            cur.close()
            connection.close()
            
            # Redirigir a página de pago fallido
            return redirect("/pago-fallido.html")
        
        if not token_ws:
            return jsonify({'error': 'Token no recibido'}), 400
        
        # Confirmar transacción en Webpay
        response = tx_handler.commit(token_ws)
        
        # Buscar la transacción en nuestra BD
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("""
            SELECT * FROM transacciones_webpay 
            WHERE token = %s
        """, (token_ws,))
        
        transaccion = cur.fetchone()
        
        if not transaccion:
            cur.close()
            connection.close()
            return jsonify({'error': 'Transacción no encontrada'}), 404
        
        # Verificar si el pago fue exitoso (response_code == 0)
        if response['response_code'] == 0:
            # Pago exitoso - actualizar reserva a 'activa'
            cur.execute("""
                UPDATE reservas 
                SET estado = 'activa' 
                WHERE id = %s
            """, (transaccion['reserva_id'],))
            
            cur.execute("""
                UPDATE transacciones_webpay 
                SET estado = 'aprobada' 
                WHERE id = %s
            """, (transaccion['id'],))
            
            connection.commit()
            
            # Obtener datos de la reserva y usuario para notificación
            cur.execute("""
                SELECT 
                    r.*, 
                    u.username, u.email, u.telefono, u.nombre, u.apellido,
                    e.nombre as nombre_entrenador
                FROM reservas r
                JOIN usuarios u ON r.usuario_id = u.id
                LEFT JOIN entrenadores e ON r.entrenador_id = e.id
                WHERE r.id = %s
            """, (transaccion['reserva_id'],))
            
            reserva_completa = cur.fetchone()
            
            if reserva_completa:
                # Preparar datos para notificación
                usuario_data = {
                    'nombre': reserva_completa.get('nombre') or reserva_completa.get('username'),
                    'email': reserva_completa.get('email'),
                    'telefono': reserva_completa.get('telefono')
                }
                
                reserva_data = {
                    'fecha': str(reserva_completa['fecha']),
                    'hora': str(reserva_completa['hora'])[0:5],  # HH:MM
                    'actividad': reserva_completa['actividad'],
                    'entrenador': reserva_completa.get('nombre_entrenador') or 'Sin entrenador',
                    'precio': transaccion['amount']
                }
                
                # Enviar notificaciones (email + SMS)
                try:
                    resultado = notificaciones.notificar_reserva_confirmada(usuario_data, reserva_data)
                    print(f"[NOTIF] Email: {'✓' if resultado['email'] else 'X'}, SMS: {'✓' if resultado['sms'] else 'X'}")
                except Exception as e:
                    print(f"[WARN] Error al enviar notificaciones: {e}")
            
            cur.close()
            connection.close()
            
            # Redirigir al usuario a una página de éxito (mismo directorio)
            return redirect(f"/pago-exitoso.html?reserva_id={transaccion['reserva_id']}")
        else:
            # Pago rechazado - marcar reserva como cancelada
            cur.execute("""
                UPDATE reservas 
                SET estado = 'cancelada' 
                WHERE id = %s
            """, (transaccion['reserva_id'],))
            
            cur.execute("""
                UPDATE transacciones_webpay 
                SET estado = 'rechazada' 
                WHERE id = %s
            """, (transaccion['id'],))
            
            connection.commit()
            
            return redirect("/pago-fallido.html")
        
        cur.close()
        connection.close()
        
    except Exception as e:
        print(f"Error confirmando transacción: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== RESERVAS (CLIENTE) ====================
@app.route('/api/reservas/<int:user_id>', methods=['GET'])
def get_reservas(user_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("""
            SELECT r.*, e.nombre as nombre_entrenador 
            FROM reservas r
            LEFT JOIN entrenadores e ON r.entrenador_id = e.id
            WHERE r.usuario_id = %s AND r.estado = 'activa'
            ORDER BY r.fecha, r.hora
        """, (user_id,))
        reservas = cur.fetchall()
        cur.close()
        connection.close()
        
        # Convertir timedelta a string
        for reserva in reservas:
            if 'hora' in reserva and reserva['hora']:
                reserva['hora'] = str(reserva['hora'])
            if 'fecha' in reserva and reserva['fecha']:
                reserva['fecha'] = str(reserva['fecha'])
            if 'fecha_creacion' in reserva and reserva['fecha_creacion']:
                reserva['fecha_creacion'] = str(reserva['fecha_creacion'])
            if 'fecha_modificacion' in reserva and reserva['fecha_modificacion']:
                reserva['fecha_modificacion'] = str(reserva['fecha_modificacion'])
        
        return jsonify(reservas), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reservas/<int:reserva_id>', methods=['DELETE'])
def cancelar_reserva(reserva_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        # Obtener datos completos de la reserva antes de cancelar
        cur.execute("""
            SELECT 
                r.*, 
                u.username, u.email, u.telefono, u.nombre, u.apellido,
                e.nombre as nombre_entrenador
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN entrenadores e ON r.entrenador_id = e.id
            WHERE r.id = %s
        """, (reserva_id,))
        reserva = cur.fetchone()
        
        if not reserva:
            cur.close()
            connection.close()
            return jsonify({'error': 'Reserva no encontrada'}), 404
        
        # Determinar motivo de cancelación (del request body)
        data = request.json or {}
        motivo = data.get('motivo', 'cancelacion')  # 'cancelacion' o 'reembolso'
        
        cur.execute("""
            UPDATE reservas 
            SET estado = 'cancelada', fecha_modificacion = NOW()
            WHERE id = %s
        """, (reserva_id,))
        
        connection.commit()
        
        # Enviar notificaciones
        usuario_data = {
            'nombre': reserva.get('nombre') or reserva.get('username'),
            'email': reserva.get('email'),
            'telefono': reserva.get('telefono')
        }
        
        reserva_data = {
            'fecha': str(reserva['fecha']),
            'hora': str(reserva['hora'])[0:5],
            'actividad': reserva['actividad'],
            'entrenador': reserva.get('nombre_entrenador') or 'Sin entrenador'
        }
        
        try:
            resultado = notificaciones.notificar_cancelacion(usuario_data, reserva_data, motivo)
            print(f"[NOTIF] Cancelación - Email: {'✓' if resultado['email'] else 'X'}, SMS: {'✓' if resultado['sms'] else 'X'}")
        except Exception as e:
            print(f"[WARN] Error al enviar notificaciones de cancelación: {e}")
        
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Reserva cancelada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== HISTORIAL (CLIENTE) ====================
@app.route('/api/historial/<int:user_id>', methods=['GET'])
def get_historial(user_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("""
            SELECT r.*, e.nombre as nombre_entrenador 
            FROM reservas r
            LEFT JOIN entrenadores e ON r.entrenador_id = e.id
            WHERE r.usuario_id = %s
            ORDER BY r.fecha_creacion DESC
        """, (user_id,))
        historial = cur.fetchall()
        cur.close()
        connection.close()
        
        for reserva in historial:
            if 'hora' in reserva and reserva['hora']:
                reserva['hora'] = str(reserva['hora'])
            if 'fecha' in reserva and reserva['fecha']:
                reserva['fecha'] = str(reserva['fecha'])
            if 'fecha_creacion' in reserva and reserva['fecha_creacion']:
                reserva['fecha_creacion'] = str(reserva['fecha_creacion'])
            if 'fecha_modificacion' in reserva and reserva['fecha_modificacion']:
                reserva['fecha_modificacion'] = str(reserva['fecha_modificacion'])
        
        return jsonify(historial), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== BLOQUES (ADMIN) ====================
@app.route('/api/cupos', methods=['GET'])
def get_cupos():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("""
            SELECT * FROM cupos
            WHERE disponible = TRUE
            ORDER BY fecha, hora
        """)
        cupos = cur.fetchall()
        cur.close()
        connection.close()
        
        for cupo in cupos:
            if 'hora' in cupo and cupo['hora']:
                cupo['hora'] = str(cupo['hora'])
            if 'fecha' in cupo and cupo['fecha']:
                cupo['fecha'] = str(cupo['fecha'])
            if 'fecha_creacion' in cupo and cupo['fecha_creacion']:
                cupo['fecha_creacion'] = str(cupo['fecha_creacion'])
        
        return jsonify(cupos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bloques', methods=['GET'])
def get_bloques():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("""
            SELECT b.*, e.nombre as nombre_entrenador 
            FROM bloques b
            LEFT JOIN entrenadores e ON b.entrenador_id = e.id
            ORDER BY b.fecha, b.hora
        """)
        bloques = cur.fetchall()
        cur.close()
        connection.close()
        
        for bloque in bloques:
            if 'hora' in bloque and bloque['hora']:
                bloque['hora'] = str(bloque['hora'])
            if 'fecha' in bloque and bloque['fecha']:
                bloque['fecha'] = str(bloque['fecha'])
            if 'fecha_creacion' in bloque and bloque['fecha_creacion']:
                bloque['fecha_creacion'] = str(bloque['fecha_creacion'])
        
        return jsonify(bloques), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bloques', methods=['POST'])
def crear_bloque():
    try:
        data = request.json
        actividad = data.get('actividad')
        fecha = data.get('fecha')
        hora = data.get('hora')
        entrenador_nombre = data.get('entrenador')
        cupos = data.get('cupos')
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("SELECT id FROM entrenadores WHERE nombre = %s", (entrenador_nombre,))
        entrenador = cur.fetchone()
        
        if not entrenador:
            cur.close()
            connection.close()
            return jsonify({'error': 'Entrenador no encontrado'}), 404
        
        entrenador_id = entrenador['id']
        
        cur.execute("""
            INSERT INTO bloques (actividad, fecha, hora, entrenador_id, cupos_totales, cupos_disponibles)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (actividad, fecha, hora, entrenador_id, cupos, cupos))
        
        connection.commit()
        bloque_id = cur.lastrowid
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'bloque_id': bloque_id,
            'message': 'Bloque creado exitosamente'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENTRENADORES ====================
@app.route('/api/entrenadores', methods=['GET'])
def get_entrenadores():
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("SELECT * FROM entrenadores")
        entrenadores = cur.fetchall()
        cur.close()
        connection.close()
        
        return jsonify(entrenadores), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ALUMNOS POR ENTRENADOR ====================
@app.route('/api/entrenador/<string:nombre>/alumnos', methods=['GET'])
def get_alumnos_entrenador(nombre):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute("""
            SELECT DISTINCT u.username, u.id
            FROM usuarios u
            INNER JOIN reservas r ON u.id = r.usuario_id
            INNER JOIN entrenadores e ON r.entrenador_id = e.id
            WHERE e.nombre = %s AND r.estado = 'activa'
        """, (nombre,))
        alumnos = cur.fetchall()
        cur.close()
        connection.close()
        
        return jsonify(alumnos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== REAGENDAR RESERVA ====================
@app.route('/api/reservas/<int:reserva_id>/reagendar', methods=['POST'])
def reagendar_reserva(reserva_id):
    """
    Endpoint específico para reagendamiento que cancela la reserva vieja,
    crea una nueva y envía notificación de reagendamiento
    """
    try:
        data = request.json
        nuevo_bloque_id = data.get('nuevo_bloque_id')
        usuario_id = data.get('usuario_id')
        
        if not nuevo_bloque_id or not usuario_id:
            return jsonify({'error': 'Faltan datos requeridos'}), 400
        
        connection = get_db_connection()
        cur = connection.cursor()
        
        # 1. Obtener datos de la reserva vieja
        cur.execute("""
            SELECT 
                r.*, 
                u.username, u.email, u.telefono, u.nombre, u.apellido,
                e.nombre as nombre_entrenador
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN entrenadores e ON r.entrenador_id = e.id
            WHERE r.id = %s AND r.usuario_id = %s
        """, (reserva_id, usuario_id))
        reserva_vieja = cur.fetchone()
        
        if not reserva_vieja:
            cur.close()
            connection.close()
            return jsonify({'error': 'Reserva no encontrada'}), 404
        
        # 2. Obtener datos del nuevo bloque
        if nuevo_bloque_id == 'sin_entrenador':
            # Caso sin entrenador
            nueva_actividad = data.get('actividad')
            nueva_fecha = data.get('fecha')
            nueva_hora = data.get('hora')
            nuevo_entrenador_id = None
            nuevo_entrenador_nombre = 'Sin entrenador'
            
            if len(nueva_hora.split(':')) == 2:
                nueva_hora = nueva_hora + ':00'
        else:
            # Caso con entrenador (bloque normal)
            cur.execute("""
                SELECT b.*, e.nombre as nombre_entrenador, e.id as entrenador_id
                FROM bloques b
                LEFT JOIN entrenadores e ON b.entrenador_id = e.id
                WHERE b.id = %s
            """, (nuevo_bloque_id,))
            nuevo_bloque = cur.fetchone()
            
            if not nuevo_bloque:
                cur.close()
                connection.close()
                return jsonify({'error': 'Nuevo bloque no encontrado'}), 404
            
            nueva_actividad = nuevo_bloque['actividad']
            nueva_fecha = str(nuevo_bloque['fecha'])
            nueva_hora = str(nuevo_bloque['hora'])
            nuevo_entrenador_id = nuevo_bloque['entrenador_id']
            nuevo_entrenador_nombre = nuevo_bloque['nombre_entrenador']
        
        # 3. Cancelar reserva vieja
        cur.execute("""
            UPDATE reservas 
            SET estado = 'cancelada', fecha_modificacion = NOW()
            WHERE id = %s
        """, (reserva_id,))
        
        # 4. Crear nueva reserva con estado 'activa' (ya pagó antes)
        cur.execute("""
            INSERT INTO reservas (usuario_id, actividad, fecha, hora, entrenador_id, estado, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, 'activa', NOW())
        """, (usuario_id, nueva_actividad, nueva_fecha, nueva_hora, nuevo_entrenador_id))
        
        nueva_reserva_id = cur.lastrowid
        connection.commit()
        
        # 5. Enviar notificación de reagendamiento
        usuario_data = {
            'nombre': reserva_vieja.get('nombre') or reserva_vieja.get('username'),
            'email': reserva_vieja.get('email'),
            'telefono': reserva_vieja.get('telefono')
        }
        
        reserva_vieja_data = {
            'fecha': str(reserva_vieja['fecha']),
            'hora': str(reserva_vieja['hora'])[0:5],
            'actividad': reserva_vieja['actividad'],
            'entrenador': reserva_vieja.get('nombre_entrenador') or 'Sin entrenador'
        }
        
        reserva_nueva_data = {
            'fecha': nueva_fecha,
            'hora': nueva_hora[0:5],
            'actividad': nueva_actividad,
            'entrenador': nuevo_entrenador_nombre
        }
        
        try:
            resultado = notificaciones.notificar_reagendamiento(usuario_data, reserva_vieja_data, reserva_nueva_data)
            print(f"[NOTIF] Reagendamiento - Email: {'✓' if resultado['email'] else 'X'}, SMS: {'✓' if resultado['sms'] else 'X'}")
        except Exception as e:
            print(f"[WARN] Error al enviar notificaciones de reagendamiento: {e}")
        
        cur.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Reserva reagendada exitosamente',
            'nueva_reserva_id': nueva_reserva_id
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PROGRESO (CLIENTE) ====================
@app.route('/api/progreso/<int:user_id>', methods=['GET'])
def get_progreso(user_id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN fecha < CURDATE() THEN 1 ELSE 0 END) as completadas
            FROM reservas
            WHERE usuario_id = %s AND estado = 'activa'
        """, (user_id,))
        
        resultado = cur.fetchone()
        cur.close()
        connection.close()
        
        total = resultado['total'] if resultado['total'] else 0
        completadas = resultado['completadas'] if resultado['completadas'] else 0
        
        porcentaje = (completadas / total * 100) if total > 0 else 0
        
        return jsonify({
            'total': total,
            'completadas': completadas,
            'porcentaje': round(porcentaje, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== SERVIR ARCHIVOS ESTÁTICOS ====================
@app.route('/pago-exitoso.html')
def pago_exitoso():
    return send_from_directory('.', 'pago-exitoso.html')

@app.route('/pago-fallido.html')
def pago_fallido():
    return send_from_directory('.', 'pago-fallido.html')

@app.route('/confirmar-reserva.html')
def confirmar_reserva():
    return send_from_directory('.', 'confirmar-reserva.html')

@app.route('/style.css')
def serve_css():
    return send_from_directory('.', 'style.css')

@app.route('/Fondo%20Gym.jpeg')
@app.route('/Fondo Gym.jpeg')
def serve_background():
    return send_from_directory('.', 'Fondo Gym.jpeg')

@app.route('/script_integrado.js')
def serve_script_integrado():
    return send_from_directory('.', 'script_integrado.js')

@app.route('/script.js')
def serve_script():
    return send_from_directory('.', 'script.js')

# ==================== RUTA PRINCIPAL ====================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    precio_actual = obtener_precio_reserva()
    print("=" * 60)
    print("GIMNASIO PRO FUNCIONAL - BACKEND CON WEBPAY")
    print("=" * 60)
    print(f"Ambiente Webpay: {webpay_config.WEBPAY_ENVIRONMENT}")
    print(f"Precio por reserva: ${precio_actual:,} CLP (desde Base de Datos)")
    print("=" * 60)
    app.run(debug=config.DEBUG, port=config.PORT)

