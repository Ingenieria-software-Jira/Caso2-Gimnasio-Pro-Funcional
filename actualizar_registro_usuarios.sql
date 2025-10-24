-- ==========================================
-- ACTUALIZAR TABLA DE USUARIOS PARA REGISTRO COMPLETO
-- ==========================================

USE gimnasio_db;

-- Agregar columnas necesarias para el registro completo
ALTER TABLE usuarios 
ADD COLUMN IF NOT EXISTS nombre VARCHAR(100) AFTER username,
ADD COLUMN IF NOT EXISTS apellido VARCHAR(100) AFTER nombre,
ADD COLUMN IF NOT EXISTS email VARCHAR(150) UNIQUE AFTER apellido,
ADD COLUMN IF NOT EXISTS password VARCHAR(255) AFTER email,
ADD COLUMN IF NOT EXISTS telefono VARCHAR(20) AFTER password,
ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE AFTER telefono;

-- Crear índice para email (búsquedas más rápidas)
CREATE INDEX IF NOT EXISTS idx_email ON usuarios(email);

-- Actualizar usuarios existentes sin estos datos (opcional, solo para evitar problemas)
-- Los usuarios que ya existen sin estos campos pueden seguir usando el sistema

