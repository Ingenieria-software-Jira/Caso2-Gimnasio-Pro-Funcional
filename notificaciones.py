"""
Sistema de notificaciones para Gimnasio Pro Funcional
Envío de confirmaciones por Email (Gmail SMTP) y SMS (Twilio)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import notificaciones_config as config

# ==================== CONFIGURACIÓN TWILIO ====================
try:
    twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    print("[OK] Cliente Twilio inicializado correctamente")
except Exception as e:
    print(f"[WARN] Error al inicializar Twilio: {e}")
    twilio_client = None


# ==================== FUNCIONES DE ENVÍO ====================

def enviar_email(destinatario, asunto, mensaje_html, mensaje_texto=None):
    """
    Envía un email usando Gmail SMTP
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del email
        mensaje_html: Contenido HTML del email
        mensaje_texto: Contenido en texto plano (opcional)
    
    Returns:
        True si se envió correctamente, False si hubo error
    """
    if not config.EMAIL_ENABLED or not config.NOTIFICATIONS_ENABLED:
        print(f"[INFO] Emails deshabilitados - No se envió a {destinatario}")
        return False
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = config.GMAIL_EMAIL
        msg['To'] = destinatario
        msg['Subject'] = asunto
        
        # Agregar contenido
        if mensaje_texto:
            part1 = MIMEText(mensaje_texto, 'plain', 'utf-8')
            msg.attach(part1)
        
        part2 = MIMEText(mensaje_html, 'html', 'utf-8')
        msg.attach(part2)
        
        # Conectar y enviar
        server = smtplib.SMTP(config.GMAIL_SMTP_SERVER, config.GMAIL_SMTP_PORT)
        server.starttls()
        server.login(config.GMAIL_EMAIL, config.GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"[OK] Email enviado a {destinatario}")
        return True
        
    except Exception as e:
        print(f"[ERROR] No se pudo enviar email a {destinatario}: {e}")
        return False


def enviar_sms(numero, mensaje):
    """
    Envía un SMS usando Twilio
    
    Args:
        numero: Número de teléfono con formato +56912345678
        mensaje: Texto del mensaje (máximo 160 caracteres recomendado)
    
    Returns:
        True si se envió correctamente, False si hubo error
    """
    if not config.SMS_ENABLED or not config.NOTIFICATIONS_ENABLED:
        print(f"[INFO] SMS deshabilitados - No se envió a {numero}")
        return False
    
    if not twilio_client:
        print(f"[ERROR] Cliente Twilio no inicializado")
        return False
    
    # Verificar si el número está en la lista de verificados (trial account)
    if numero not in config.VERIFIED_PHONE_NUMBERS:
        print(f"[WARN] Número {numero} no verificado en Twilio Trial. SMS no enviado.")
        print(f"[INFO] Números verificados: {config.VERIFIED_PHONE_NUMBERS}")
        return False
    
    try:
        message = twilio_client.messages.create(
            body=mensaje,
            from_=config.TWILIO_PHONE_NUMBER,
            to=numero
        )
        
        print(f"[OK] SMS enviado a {numero} (SID: {message.sid})")
        return True
        
    except Exception as e:
        print(f"[ERROR] No se pudo enviar SMS a {numero}: {e}")
        return False


# ==================== PLANTILLAS DE NOTIFICACIONES ====================

def notificar_reserva_confirmada(usuario_data, reserva_data):
    """
    Envía notificación de confirmación de reserva (después del pago exitoso)
    
    Args:
        usuario_data: dict con 'email', 'nombre', 'telefono'
        reserva_data: dict con 'fecha', 'hora', 'actividad', 'entrenador', 'precio'
    """
    # EMAIL
    asunto = f"✅ Reserva Confirmada - Gimnasio Pro Funcional"
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #e74c3c, #c0392b); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎉 ¡Reserva Confirmada!</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <p style="font-size: 16px;">Hola <strong>{usuario_data.get('nombre', 'Cliente')}</strong>,</p>
                
                <p>Tu pago ha sido procesado exitosamente. Aquí están los detalles de tu reserva:</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>📅 Fecha:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['fecha']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>🕐 Hora:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['hora']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>🏋️ Actividad:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['actividad']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>👤 Entrenador:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['entrenador']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>💰 Total Pagado:</strong></td>
                            <td style="padding: 10px; color: #27ae60; font-size: 18px; font-weight: bold;">${reserva_data.get('precio', 0)} CLP</td>
                        </tr>
                    </table>
                </div>
                
                <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>⚠️ Recuerda:</strong></p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Llega 5 minutos antes</li>
                        <li>Trae tu toalla y botella de agua</li>
                        <li>Para cancelar, avisa con 2 horas de anticipación</li>
                    </ul>
                </div>
                
                <p style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                    ¡Nos vemos en el gimnasio! 💪<br>
                    <strong>Gimnasio Pro Funcional</strong>
                </p>
            </div>
        </body>
    </html>
    """
    
    mensaje_texto = f"""
    RESERVA CONFIRMADA - Gimnasio Pro Funcional
    
    Hola {usuario_data.get('nombre', 'Cliente')},
    
    Tu pago ha sido procesado exitosamente.
    
    Detalles de tu reserva:
    - Fecha: {reserva_data['fecha']}
    - Hora: {reserva_data['hora']}
    - Actividad: {reserva_data['actividad']}
    - Entrenador: {reserva_data['entrenador']}
    - Total Pagado: ${reserva_data.get('precio', 0)} CLP
    
    Recuerda llegar 5 minutos antes.
    
    ¡Nos vemos en el gimnasio!
    """
    
    # SMS
    mensaje_sms = f"✅ Reserva confirmada! {reserva_data['fecha']} a las {reserva_data['hora']} - {reserva_data['actividad']} con {reserva_data['entrenador']}. ¡Te esperamos! - Gimnasio Pro"
    
    # Enviar notificaciones
    email_enviado = enviar_email(usuario_data.get('email'), asunto, mensaje_html, mensaje_texto)
    sms_enviado = False
    
    if usuario_data.get('telefono'):
        sms_enviado = enviar_sms(usuario_data.get('telefono'), mensaje_sms)
    
    return {'email': email_enviado, 'sms': sms_enviado}


def notificar_cancelacion(usuario_data, reserva_data, motivo='cancelacion'):
    """
    Envía notificación de cancelación de reserva
    
    Args:
        usuario_data: dict con 'email', 'nombre', 'telefono'
        reserva_data: dict con 'fecha', 'hora', 'actividad', 'entrenador'
        motivo: 'cancelacion' o 'reembolso'
    """
    titulo = "Cancelación Confirmada" if motivo == 'cancelacion' else "Solicitud de Reembolso Recibida"
    emoji = "❌" if motivo == 'cancelacion' else "💰"
    
    # EMAIL
    asunto = f"{emoji} {titulo} - Gimnasio Pro Funcional"
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #95a5a6, #7f8c8d); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">{emoji} {titulo}</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <p style="font-size: 16px;">Hola <strong>{usuario_data.get('nombre', 'Cliente')}</strong>,</p>
                
                <p>Tu reserva ha sido cancelada exitosamente.</p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>📅 Fecha:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['fecha']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>🕐 Hora:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['hora']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;"><strong>🏋️ Actividad:</strong></td>
                            <td style="padding: 10px; border-bottom: 1px solid #dee2e6;">{reserva_data['actividad']}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;"><strong>👤 Entrenador:</strong></td>
                            <td style="padding: 10px;">{reserva_data['entrenador']}</td>
                        </tr>
                    </table>
                </div>
                
                {'<p><strong>Tu reembolso será procesado en 5-7 días hábiles.</strong></p>' if motivo == 'reembolso' else ''}
                
                <p style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                    Esperamos verte pronto 💪<br>
                    <strong>Gimnasio Pro Funcional</strong>
                </p>
            </div>
        </body>
    </html>
    """
    
    # SMS
    mensaje_sms = f"{emoji} Reserva cancelada: {reserva_data['fecha']} {reserva_data['hora']}. {'Reembolso en 5-7 días.' if motivo == 'reembolso' else 'Esperamos verte pronto!'} - Gimnasio Pro"
    
    # Enviar notificaciones
    email_enviado = enviar_email(usuario_data.get('email'), asunto, mensaje_html)
    sms_enviado = False
    
    if usuario_data.get('telefono'):
        sms_enviado = enviar_sms(usuario_data.get('telefono'), mensaje_sms)
    
    return {'email': email_enviado, 'sms': sms_enviado}


def notificar_reagendamiento(usuario_data, reserva_vieja, reserva_nueva):
    """
    Envía notificación de reagendamiento de reserva
    
    Args:
        usuario_data: dict con 'email', 'nombre', 'telefono'
        reserva_vieja: dict con fecha/hora anterior
        reserva_nueva: dict con fecha/hora nueva
    """
    # EMAIL
    asunto = "🔄 Reserva Reagendada - Gimnasio Pro Funcional"
    
    mensaje_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #3498db, #2980b9); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🔄 Reserva Reagendada</h1>
            </div>
            
            <div style="padding: 30px; background: #f8f9fa;">
                <p style="font-size: 16px;">Hola <strong>{usuario_data.get('nombre', 'Cliente')}</strong>,</p>
                
                <p>Tu reserva ha sido reagendada exitosamente.</p>
                
                <div style="background: #ffebee; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #c0392b;"><strong>❌ Reserva Anterior (Cancelada):</strong></p>
                    <p style="margin: 5px 0;">{reserva_vieja['fecha']} a las {reserva_vieja['hora']}</p>
                </div>
                
                <div style="background: #e8f5e9; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #27ae60;"><strong>✅ Nueva Reserva:</strong></p>
                    <table style="width: 100%; margin-top: 10px;">
                        <tr>
                            <td><strong>📅 Fecha:</strong></td>
                            <td>{reserva_nueva['fecha']}</td>
                        </tr>
                        <tr>
                            <td><strong>🕐 Hora:</strong></td>
                            <td>{reserva_nueva['hora']}</td>
                        </tr>
                        <tr>
                            <td><strong>🏋️ Actividad:</strong></td>
                            <td>{reserva_nueva['actividad']}</td>
                        </tr>
                        <tr>
                            <td><strong>👤 Entrenador:</strong></td>
                            <td>{reserva_nueva['entrenador']}</td>
                        </tr>
                    </table>
                </div>
                
                <p style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
                    ¡Nos vemos en tu nueva fecha! 💪<br>
                    <strong>Gimnasio Pro Funcional</strong>
                </p>
            </div>
        </body>
    </html>
    """
    
    # SMS
    mensaje_sms = f"🔄 Reserva reagendada! Nueva fecha: {reserva_nueva['fecha']} {reserva_nueva['hora']} - {reserva_nueva['actividad']}. ¡Te esperamos! - Gimnasio Pro"
    
    # Enviar notificaciones
    email_enviado = enviar_email(usuario_data.get('email'), asunto, mensaje_html)
    sms_enviado = False
    
    if usuario_data.get('telefono'):
        sms_enviado = enviar_sms(usuario_data.get('telefono'), mensaje_sms)
    
    return {'email': email_enviado, 'sms': sms_enviado}


# ==================== FUNCIÓN DE PRUEBA ====================

if __name__ == '__main__':
    print("\n=== PRUEBA DEL SISTEMA DE NOTIFICACIONES ===\n")
    
    # Datos de prueba
    usuario_test = {
        'nombre': 'Sebastian',
        'email': 'gim.pro878@gmail.com',
        'telefono': '+56951595450'
    }
    
    reserva_test = {
        'fecha': '2025-10-28',
        'hora': '15:00',
        'actividad': 'Cardio',
        'entrenador': 'Ricardo Meruane',
        'precio': 5000
    }
    
    print("1. Probando notificación de confirmación de reserva...")
    resultado = notificar_reserva_confirmada(usuario_test, reserva_test)
    print(f"   Email: {'✅' if resultado['email'] else '❌'}")
    print(f"   SMS: {'✅' if resultado['sms'] else '❌'}\n")
    
    print("=== PRUEBA COMPLETADA ===\n")

