"""
Funciones helper para manejo de base de datos
Gimnasio Pro Funcional
"""
import pymysql
import config
from contextlib import contextmanager

@contextmanager
def get_db_connection():
    """
    Context manager para manejar conexiones a la base de datos de forma segura
    
    Uso:
        with get_db_connection() as (connection, cursor):
            cursor.execute("SELECT * FROM tabla")
            results = cursor.fetchall()
    """
    connection = None
    cursor = None
    try:
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DB,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()
        yield connection, cursor
        connection.commit()
    except Exception as e:
        if connection:
            connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def obtener_usuario_completo(usuario_id):
    """
    Obtiene información completa de un usuario incluyendo datos de contacto
    
    Args:
        usuario_id (int): ID del usuario
        
    Returns:
        dict: Datos del usuario o None si no existe
    """
    with get_db_connection() as (connection, cursor):
        cursor.execute("""
            SELECT id, username, nombre, apellido, email, telefono, rol
            FROM usuarios 
            WHERE id = %s
        """, (usuario_id,))
        return cursor.fetchone()


def obtener_reserva_completa(reserva_id):
    """
    Obtiene información completa de una reserva incluyendo usuario y entrenador
    
    Args:
        reserva_id (int): ID de la reserva
        
    Returns:
        dict: Datos completos de la reserva o None si no existe
    """
    with get_db_connection() as (connection, cursor):
        cursor.execute("""
            SELECT 
                r.*, 
                u.username, u.email, u.telefono, u.nombre as usuario_nombre, u.apellido,
                e.nombre as nombre_entrenador
            FROM reservas r
            JOIN usuarios u ON r.usuario_id = u.id
            LEFT JOIN entrenadores e ON r.entrenador_id = e.id
            WHERE r.id = %s
        """, (reserva_id,))
        return cursor.fetchone()


def obtener_bloque_completo(bloque_id):
    """
    Obtiene información completa de un bloque incluyendo entrenador
    
    Args:
        bloque_id (int): ID del bloque
        
    Returns:
        dict: Datos completos del bloque o None si no existe
    """
    with get_db_connection() as (connection, cursor):
        cursor.execute("""
            SELECT b.*, e.nombre as nombre_entrenador, e.id as entrenador_id
            FROM bloques b
            LEFT JOIN entrenadores e ON b.entrenador_id = e.id
            WHERE b.id = %s
        """, (bloque_id,))
        return cursor.fetchone()


def preparar_datos_usuario_para_notificacion(usuario_data):
    """
    Prepara los datos del usuario en el formato necesario para notificaciones
    
    Args:
        usuario_data (dict): Datos del usuario de la BD
        
    Returns:
        dict: Datos formateados para el sistema de notificaciones
    """
    return {
        'nombre': usuario_data.get('nombre') or usuario_data.get('usuario_nombre') or usuario_data.get('username'),
        'email': usuario_data.get('email'),
        'telefono': usuario_data.get('telefono')
    }


def preparar_datos_reserva_para_notificacion(reserva_data, precio=None):
    """
    Prepara los datos de la reserva en el formato necesario para notificaciones
    
    Args:
        reserva_data (dict): Datos de la reserva de la BD
        precio (int, optional): Precio a mostrar. Si no se proporciona, no se incluye
        
    Returns:
        dict: Datos formateados para el sistema de notificaciones
    """
    datos = {
        'fecha': str(reserva_data['fecha']),
        'hora': str(reserva_data['hora'])[0:5],  # HH:MM
        'actividad': reserva_data['actividad'],
        'entrenador': reserva_data.get('nombre_entrenador') or 'Sin entrenador'
    }
    
    if precio is not None:
        datos['precio'] = precio
        
    return datos


def obtener_precio_actual():
    """
    Obtiene el precio actual de reserva desde la configuración en BD
    
    Returns:
        int: Precio actual de reserva
    """
    try:
        with get_db_connection() as (connection, cursor):
            cursor.execute("""
                SELECT valor FROM configuracion 
                WHERE nombre = 'precio_reserva'
            """)
            result = cursor.fetchone()
            
            if result:
                return int(result['valor'])
            else:
                print("[WARN] No se encontró precio_reserva en configuración, usando 1000 por defecto")
                return 1000
    except Exception as e:
        print(f"[ERROR] Error al obtener precio desde BD: {e}")
        return 1000


def actualizar_estado_reserva(reserva_id, nuevo_estado):
    """
    Actualiza el estado de una reserva
    
    Args:
        reserva_id (int): ID de la reserva
        nuevo_estado (str): Nuevo estado ('activa', 'cancelada', 'pendiente_pago')
        
    Returns:
        bool: True si se actualizó correctamente
    """
    with get_db_connection() as (connection, cursor):
        cursor.execute("""
            UPDATE reservas 
            SET estado = %s, fecha_modificacion = NOW()
            WHERE id = %s
        """, (nuevo_estado, reserva_id))
        return cursor.rowcount > 0


def crear_reserva(usuario_id, actividad, fecha, hora, entrenador_id, estado='activa'):
    """
    Crea una nueva reserva en la base de datos
    
    Args:
        usuario_id (int): ID del usuario
        actividad (str): Tipo de actividad ('Cardio' o 'Fuerza')
        fecha (str): Fecha de la reserva (YYYY-MM-DD)
        hora (str): Hora de la reserva (HH:MM:SS)
        entrenador_id (int or None): ID del entrenador o None si es sin entrenador
        estado (str): Estado inicial de la reserva
        
    Returns:
        int: ID de la reserva creada
    """
    with get_db_connection() as (connection, cursor):
        cursor.execute("""
            INSERT INTO reservas (usuario_id, actividad, fecha, hora, entrenador_id, estado, fecha_creacion)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (usuario_id, actividad, fecha, hora, entrenador_id, estado))
        return cursor.lastrowid

