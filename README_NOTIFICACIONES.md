# 📧📱 Sistema de Notificaciones - Gimnasio Pro Funcional

Sistema completo de notificaciones automáticas por **Email** (Gmail SMTP) y **SMS** (Twilio).

---

## ✅ **Estado: IMPLEMENTADO Y FUNCIONAL**

### **Notificaciones Implementadas:**

1. ✅ **Confirmación de Reserva** (después del pago exitoso)
   - Email con detalles completos de la reserva
   - SMS con confirmación breve
   
2. ✅ **Cancelación de Reserva**
   - Email y SMS confirmando la cancelación
   
3. ✅ **Solicitud de Reembolso**
   - Email y SMS indicando que el reembolso será procesado en 5-7 días
   
4. ✅ **Reagendamiento de Reserva**
   - Email y SMS mostrando fecha/hora anterior y nueva

---

## 🔧 **Configuración**

### **Credenciales Configuradas:**

- **Gmail:** gim.pro878@gmail.com
- **Twilio:** Account configurado con $15 USD de crédito
- **Número SMS:** +56951595450 (verificado para pruebas)

Todas las credenciales están en `notificaciones_config.py` (protegido en `.gitignore`)

---

## 🧪 **Cómo Probar**

### **Opción 1: Usar el Script de Prueba**

```bash
python probar_notificaciones.py
```

Este script te permite probar cada tipo de notificación individualmente.

### **Opción 2: Probar en la Aplicación**

1. **Inicia el servidor:**
   ```bash
   python app_webpay.py
   ```

2. **Prueba la confirmación de reserva:**
   - Haz una reserva y completa el pago
   - Recibirás email + SMS confirmando la reserva

3. **Prueba la cancelación:**
   - Ve a "Ver horas agendadas"
   - Cancela una reserva y solicita reembolso
   - Recibirás email + SMS confirmando la cancelación

4. **Prueba el reagendamiento:**
   - Cancela una reserva y elige "Reagendar"
   - Selecciona nueva fecha/hora
   - Recibirás email + SMS con la nueva fecha

---

## 📧 **Formato de Emails**

Los emails incluyen:
- **HTML profesional** con colores del gimnasio (rojo/negro)
- **Detalles completos** de la reserva (fecha, hora, entrenador, actividad, precio)
- **Términos y condiciones** relevantes
- **Responsive design** para móviles

---

## 📱 **SMS**

Los SMS son breves y directos:
- Máximo 160 caracteres
- Incluyen fecha, hora y actividad
- Nombre del gimnasio al final

---

## ⚙️ **Habilitar/Deshabilitar**

Para deshabilitar temporalmente las notificaciones, edita `notificaciones_config.py`:

```python
NOTIFICATIONS_ENABLED = False  # Deshabilitar todas
SMS_ENABLED = False           # Solo deshabilitar SMS
EMAIL_ENABLED = False         # Solo deshabilitar emails
```

---

## 🔐 **Seguridad**

- Las credenciales están en `notificaciones_config.py`
- Este archivo está en `.gitignore` y NO se sube a GitHub
- Para producción, usar variables de entorno

---

## 🐛 **Logs**

El sistema imprime logs en consola:

```
[OK] Email enviado a gim.pro878@gmail.com
[OK] SMS enviado a +56951595450 (SID: SM...)
[NOTIF] Email: ✓, SMS: ✓
```

---

## 📊 **Límites (Cuenta Trial)**

### **Gmail:**
- ✅ 500 emails/día GRATIS

### **Twilio:**
- ✅ $15 USD de crédito inicial
- ⚠️ Solo puede enviar SMS a números verificados (trial)
- 💵 ~$0.0075 USD por SMS en Chile

Para producción, actualizar a cuenta de pago en Twilio.

---

## 🚀 **Agregar Más Números Verificados**

1. Ve a https://console.twilio.com
2. Phone Numbers → Verified Caller IDs
3. Click "Add a new number"
4. Ingresa el número con formato `+569XXXXXXXX`
5. Twilio enviará un código por SMS
6. Verifica el código
7. Agrega el número a `notificaciones_config.py`:

```python
VERIFIED_PHONE_NUMBERS = [
    '+56951595450',  # Número original
    '+56912345678'   # Nuevo número
]
```

---

## 📝 **Archivos Creados**

- `notificaciones.py` - Módulo principal de notificaciones
- `notificaciones_config.py` - Credenciales (NO en Git)
- `probar_notificaciones.py` - Script de prueba
- `README_NOTIFICACIONES.md` - Esta documentación

---

## ✨ **Mejoras Futuras** (Opcional)

- [ ] Recordatorio 2 horas antes de la clase
- [ ] Notificación cuando el admin cancela un bloque
- [ ] Templates personalizables desde la BD
- [ ] Soporte para WhatsApp (Twilio WhatsApp API)
- [ ] Panel de admin para ver estadísticas de notificaciones

---

**¡Sistema completamente funcional y listo para usar!** 🎉

