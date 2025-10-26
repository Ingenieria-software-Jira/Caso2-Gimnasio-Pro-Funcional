# 📚 API REST - Gimnasio Pro Funcional

Documentación completa de endpoints disponibles.

---

## 🔐 **Autenticación**

La API no requiere tokens por ahora. Los endpoints verifican el `usuario_id` enviado en el body.

---

## 📋 **Endpoints Disponibles**

### **1. BLOQUES**

#### `GET /api/bloques`
Obtiene lista de bloques disponibles con filtros opcionales.

**Query Parameters:**
- `fecha` (opcional): Filtra por fecha específica (YYYY-MM-DD)
- `actividad` (opcional): Filtra por actividad ('Cardio' o 'Fuerza')
- `entrenador` (opcional): Filtra por nombre del entrenador

**Ejemplo sin filtros:**
```http
GET /api/bloques
```

**Ejemplo con filtros:**
```http
GET /api/bloques?fecha=2025-10-28&actividad=Cardio
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "actividad": "Cardio",
    "fecha": "2025-10-28",
    "hora": "15:00:00",
    "nombre_entrenador": "Ricardo Meruane",
    "cupos_totales": 10,
    "cupos_disponibles": 7,
    "fecha_creacion": "2025-10-26 10:00:00"
  }
]
```

---

### **2. CREAR RESERVA (CON PAGO)**

#### `POST /api/webpay/crear`
Crea una transacción de Webpay y reserva pendiente de pago.

**Request Body:**
```json
{
  "usuario_id": 21,
  "bloque_id": 5
}
```

**Para reservas sin entrenador:**
```json
{
  "usuario_id": 21,
  "bloque_id": "sin_entrenador",
  "actividad": "Cardio",
  "fecha": "2025-10-28",
  "hora": "15:00"
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "url": "https://webpay3gint.transbank.cl/webpayserver/initTransaction",
  "token": "01ab...",
  "buy_order": "GYM-21-1698765432",
  "amount": 5000
}
```

**El frontend debe redireccionar a `url` con el `token`**

---

### **3. CONFIRMAR PAGO**

#### `GET/POST /api/webpay/confirmar`
Endpoint de retorno de Webpay. Confirma o rechaza la transacción.

**Query/Form Parameters:**
- `token_ws`: Token de la transacción

**Este endpoint redirecciona a:**
- `/pago-exitoso.html` - Si el pago fue aprobado
- `/pago-fallido.html` - Si el pago fue rechazado

---

### **4. LISTAR RESERVAS DE USUARIO**

#### `GET /api/reservas/<usuario_id>`
Obtiene reservas activas de un usuario.

**Ejemplo:**
```http
GET /api/reservas/21
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 42,
    "usuario_id": 21,
    "actividad": "Cardio",
    "fecha": "2025-10-28",
    "hora": "15:00:00",
    "nombre_entrenador": "Ricardo Meruane",
    "estado": "activa",
    "fecha_creacion": "2025-10-26 14:30:00"
  }
]
```

---

### **5. CANCELAR RESERVA**

#### `DELETE /api/reservas/<reserva_id>`
Cancela una reserva y envía notificaciones.

**Request Body (opcional):**
```json
{
  "motivo": "reembolso"  // O "cancelacion"
}
```

**Ejemplo:**
```http
DELETE /api/reservas/42
Content-Type: application/json

{
  "motivo": "reembolso"
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Reserva cancelada exitosamente"
}
```

**Notificaciones enviadas:**
- ✅ Email al usuario
- ✅ SMS al usuario (si está verificado)

---

### **6. REAGENDAR RESERVA**

#### `POST /api/reservas/<reserva_id>/reagendar`
Cancela la reserva actual y crea una nueva con notificaciones.

**Request Body:**
```json
{
  "usuario_id": 21,
  "nuevo_bloque_id": 10
}
```

**Para reagendar sin entrenador:**
```json
{
  "usuario_id": 21,
  "nuevo_bloque_id": "sin_entrenador",
  "actividad": "Fuerza",
  "fecha": "2025-10-29",
  "hora": "16:00"
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Reserva reagendada exitosamente",
  "nueva_reserva_id": 43
}
```

**Notificaciones enviadas:**
- ✅ Email con fecha anterior y nueva
- ✅ SMS con fecha anterior y nueva

---

### **7. HISTORIAL DE RESERVAS**

#### `GET /api/historial/<usuario_id>`
Obtiene todas las reservas (activas y canceladas) de un usuario.

**Ejemplo:**
```http
GET /api/historial/21
```

**Respuesta exitosa (200):**
```json
[
  {
    "id": 42,
    "actividad": "Cardio",
    "fecha": "2025-10-28",
    "hora": "15:00:00",
    "nombre_entrenador": "Ricardo Meruane",
    "estado": "activa",
    "fecha_creacion": "2025-10-26 14:30:00",
    "fecha_modificacion": "2025-10-26 14:30:00"
  },
  {
    "id": 41,
    "actividad": "Fuerza",
    "fecha": "2025-10-27",
    "hora": "10:00:00",
    "nombre_entrenador": "George Harris",
    "estado": "cancelada",
    "fecha_creacion": "2025-10-25 12:00:00",
    "fecha_modificacion": "2025-10-26 09:00:00"
  }
]
```

---

### **8. ENTRENADORES**

#### `GET /api/entrenadores`
Obtiene lista de todos los entrenadores.

**Respuesta exitosa (200):**
```json
[
  {
    "id": 1,
    "nombre": "Ricardo Meruane",
    "especialidad": "Entrenamiento Funcional"
  },
  {
    "id": 2,
    "nombre": "George Harris",
    "especialidad": "Fuerza y Acondicionamiento"
  }
]
```

---

### **9. LOGIN**

#### `POST /api/login`
Autenticación de usuarios.

**Request Body para Cliente/Entrenador:**
```json
{
  "email": "usuario@gmail.com",
  "password": "mipassword",
  "role": "cliente"
}
```

**Request Body para Admin:**
```json
{
  "username": "admin",
  "password": "admin123",
  "role": "admin"
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Inicio de sesión exitoso",
  "user_id": 21,
  "username": "sebastianvasquez",
  "role": "cliente"
}
```

---

### **10. REGISTRO**

#### `POST /api/registro`
Registro de nuevos usuarios.

**Request Body:**
```json
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "fecha_nacimiento": "1990-05-15",
  "email": "juan@gmail.com",
  "telefono": "+56912345678",
  "username": "juanperez",
  "password": "mipassword123",
  "role": "cliente"
}
```

**Respuesta exitosa (201):**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user_id": 22
}
```

---

### **11. CONFIGURACIÓN DE PRECIOS (ADMIN)**

#### `GET /api/admin/configuracion/precio_reserva`
Obtiene el precio actual de reserva.

**Respuesta exitosa (200):**
```json
{
  "nombre": "precio_reserva",
  "valor": 5000
}
```

#### `PUT /api/admin/configuracion/precio_reserva`
Actualiza el precio de reserva.

**Request Body:**
```json
{
  "valor": 7500
}
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "message": "Precio actualizado correctamente"
}
```

---

## ⚠️ **Códigos de Error Comunes**

| Código | Significado |
|--------|-------------|
| 400 | Bad Request - Faltan datos requeridos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

**Ejemplo de error:**
```json
{
  "error": "Faltan datos requeridos"
}
```

---

## 📱 **Notificaciones Automáticas**

Los siguientes endpoints envían notificaciones automáticamente:

- ✅ **POST /api/webpay/confirmar** → Confirmación de reserva (al aprobar pago)
- ✅ **DELETE /api/reservas/<id>** → Cancelación/Reembolso
- ✅ **POST /api/reservas/<id>/reagendar** → Reagendamiento

**Canales:**
- 📧 Email (Gmail SMTP) - Automático para todos
- 📱 SMS (Twilio) - Solo números verificados en Trial

---

## 🧪 **Testing**

**URL Base de desarrollo:**
```
http://localhost:5000/api
```

**Herramientas recomendadas:**
- Postman
- Thunder Client (VS Code)
- curl
- Navegador (para endpoints GET)

---

## 📝 **Notas**

- Todos los endpoints devuelven JSON
- Las fechas están en formato: `YYYY-MM-DD`
- Las horas están en formato: `HH:MM:SS`
- Los precios están en CLP (pesos chilenos)

---

**Última actualización:** Octubre 2025

