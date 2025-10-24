// ==========================================
// GIMNASIO PRO FUNCIONAL - VERSION INTEGRADA CON BACKEND
// ==========================================

const API_URL = 'http://localhost:5000/api';
let currentUserId = null;
let reservas = [];
let bloques = [];
let historialReservas = [];

// === MOSTRAR/OCULTAR SECCIONES DE LOGIN Y REGISTRO ===
function mostrarRegistro() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('registro-section').style.display = 'block';
}

function volverALogin() {
    document.getElementById('registro-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    // Limpiar campos de registro
    document.getElementById('reg-nombre').value = '';
    document.getElementById('reg-apellido').value = '';
    document.getElementById('reg-fecha-nacimiento').value = '';
    document.getElementById('reg-email').value = '';
    document.getElementById('reg-telefono').value = '';
    document.getElementById('reg-password').value = '';
    document.getElementById('reg-password-confirm').value = '';
}

// === TOGGLE PASSWORD FIELD ===
function togglePasswordField() {
    // Ya no se usa, pero se mantiene por compatibilidad
    // Ahora siempre se muestra el campo de contraseña
}

// === REGISTRO ===
async function registrarUsuario() {
    const nombre = document.getElementById('reg-nombre').value.trim();
    const apellido = document.getElementById('reg-apellido').value.trim();
    const fechaNacimiento = document.getElementById('reg-fecha-nacimiento').value;
    const email = document.getElementById('reg-email').value.trim();
    const telefono = document.getElementById('reg-telefono').value.trim();
    const password = document.getElementById('reg-password').value;
    const passwordConfirm = document.getElementById('reg-password-confirm').value;
    const role = document.getElementById('reg-role').value;
    
    // Generar username automáticamente: nombre + apellido (sin espacios, en minúsculas)
    const username = (nombre + apellido).toLowerCase().replace(/\s+/g, '').normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    
    // Validaciones
    if (!nombre || !apellido || !email || !telefono || !password) {
        showToast('⚠️ Todos los campos son obligatorios');
        return;
    }
    
    if (!fechaNacimiento) {
        showToast('⚠️ Debes ingresar tu fecha de nacimiento');
        return;
    }
    
    if (password !== passwordConfirm) {
        showToast('⚠️ Las contraseñas no coinciden');
        return;
    }
    
    if (password.length < 6) {
        showToast('⚠️ La contraseña debe tener al menos 6 caracteres');
        return;
    }
    
    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showToast('⚠️ Email inválido');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/registro`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                nombre,
                apellido,
                fecha_nacimiento: fechaNacimiento,
                email,
                telefono,
                username,
                password,
                role
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast(`✅ Registro exitoso! Inicia sesión con tu email`);
            setTimeout(() => volverALogin(), 2000);
        } else {
            showToast(`❌ ${data.error || 'Error al registrar usuario'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

// === LOGIN ===
async function login() {
    const role = document.getElementById('role').value;
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('password').value;
    
    if (!email) {
        showToast('⚠️ Ingresa tu email');
        return;
    }
    
    if (!password) {
        showToast('⚠️ Ingresa tu contraseña');
        return;
    }

    try {
        let response, data;
        
        // Login diferente para administradores
        if (role === 'admin') {
            response = await fetch(`${API_URL}/admin/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: email, password })
            });
            
            data = await response.json();
            
            if (data.success) {
                currentUserId = data.admin_id;
            }
        } else {
            // Login normal para clientes y entrenadores (con email)
            response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password, role })
            });

            data = await response.json();
            
            if (data.success) {
                currentUserId = data.user_id;
            }
        }

        if (data.success) {
            document.getElementById('login-section').style.display = 'none';

            if (role === 'cliente') {
                document.getElementById('cliente-section').style.display = 'block';
                await cargarReservasDelServidor();
                await cargarHistorialDelServidor();
                await cargarBloquesDisponibles();
            } else if (role === 'admin') {
                document.getElementById('admin-section').style.display = 'block';
                await cargarBloquesDelServidor();
                await cargarEntrenadoresParaAdmin();
            } else if (role === 'entrenador') {
                document.getElementById('entrenador-section').style.display = 'block';
                await mostrarAlumnosDelServidor(data.username);
            }
            
            showToast(`✅ Bienvenido ${data.nombre || email}!`);
        } else {
            showToast(`❌ ${data.error || 'Error al iniciar sesión'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

// BOTON RETROCEDER
function volverLogin(section) {
    document.getElementById(section + '-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    currentUserId = null;
}

// === FECHAS Y HORAS ===
const hoy = new Date();
const hoyStr = hoy.toISOString().split('T')[0];
document.getElementById('fecha').min = hoyStr;
document.getElementById('fecha-admin').min = hoyStr;

function llenarHoras(selectId, fechaInputId) {
    const select = document.getElementById(selectId);
    select.innerHTML = '';
    const fechaSeleccionada = new Date(document.getElementById(fechaInputId).value);
    const ahora = new Date();
    const horaActual = ahora.getHours();
    const minutoActual = ahora.getMinutes();

    for (let h = 10; h <= 21; h++) {
        if (fechaSeleccionada.toDateString() === ahora.toDateString()) {
            if (h < horaActual || (h === horaActual && minutoActual > 0)) continue;
        }
        const option = document.createElement('option');
        option.value = `${h}:00`;
        option.textContent = `${h}:00`;
        select.appendChild(option);
    }
}

document.getElementById('fecha').addEventListener('change', () => llenarHoras('hora', 'fecha'));
document.getElementById('fecha-admin').addEventListener('change', () => llenarHoras('hora-admin', 'fecha-admin'));

// Cargar bloques disponibles para sincronizar dropdowns
let bloquesDisponibles = [];

async function cargarBloquesDisponibles() {
    try {
        const response = await fetch(`${API_URL}/bloques`);
        bloquesDisponibles = await response.json();
        console.log('Bloques cargados:', bloquesDisponibles);
        actualizarDropdownsCliente();
    } catch (error) {
        console.error('Error al cargar bloques:', error);
    }
}

function actualizarDropdownsCliente() {
    const actividadSelect = document.getElementById('actividad');
    const fechaSelect = document.getElementById('fecha');
    const horaSelect = document.getElementById('hora');
    const entrenadorSelect = document.getElementById('entrenador');
    
    if (!bloquesDisponibles || bloquesDisponibles.length === 0) {
        console.log('No hay bloques disponibles aún');
        return;
    }
    
    const actividadVal = actividadSelect.value;
    const fechaVal = fechaSelect.value;
    const entrenadorVal = entrenadorSelect.value;
    
    console.log('Actualizando dropdowns con:', { actividadVal, fechaVal, entrenadorVal });
    
    // Filtrar bloques según selecciones
    let bloquesFiltrados = bloquesDisponibles.filter(b => b.cupos_disponibles > 0);
    
    if (actividadVal) {
        bloquesFiltrados = bloquesFiltrados.filter(b => b.actividad === actividadVal);
    }
    if (fechaVal) {
        bloquesFiltrados = bloquesFiltrados.filter(b => b.fecha === fechaVal);
    }
    if (entrenadorVal) {
        bloquesFiltrados = bloquesFiltrados.filter(b => b.nombre_entrenador === entrenadorVal);
    }
    
    console.log('Bloques filtrados:', bloquesFiltrados);
    
    // Actualizar opciones de hora basado en bloques disponibles
    // Solo necesitamos actividad, fecha y entrenador para filtrar horas
    if (actividadVal && fechaVal && entrenadorVal) {
        const horasDisponibles = [...new Set(bloquesFiltrados.map(b => b.hora.substring(0, 5)))];
        console.log('Horas disponibles:', horasDisponibles);
        horaSelect.innerHTML = '';
        if (horasDisponibles.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No hay horas disponibles';
            horaSelect.appendChild(option);
        } else {
            horasDisponibles.sort().forEach(h => {
                const option = document.createElement('option');
                option.value = h;
                option.textContent = h;
                horaSelect.appendChild(option);
            });
        }
    }
}

document.getElementById('actividad').addEventListener('change', actualizarDropdownsCliente);
document.getElementById('fecha').addEventListener('change', actualizarDropdownsCliente);
document.getElementById('entrenador').addEventListener('change', actualizarDropdownsCliente);

window.addEventListener('load', () => {
    document.getElementById('fecha').value = hoyStr;
    document.getElementById('fecha-admin').value = hoyStr;
    llenarHoras('hora', 'fecha');
    llenarHoras('hora-admin', 'fecha-admin');
});

// === CLIENTE ===
function mostrarCrearReserva() {
    document.getElementById('crear-reserva').style.display = 'block';
    document.getElementById('lista-reservas-section').style.display = 'none';
    document.getElementById('progreso-section').style.display = 'none';
    document.getElementById('historial-section').style.display = 'none';
}

async function cargarReservasDelServidor() {
    try {
        const response = await fetch(`${API_URL}/reservas/${currentUserId}`);
        const data = await response.json();
        reservas = data.map(r => ({
            id: r.id,
            actividad: r.actividad,
            fecha: r.fecha,
            hora: r.hora.substring(0, 5), // Convertir HH:MM:SS a HH:MM
            entrenador: r.nombre_entrenador
        }));
    } catch (error) {
        console.error('Error al cargar reservas:', error);
        showToast('Error al cargar reservas');
    }
}

async function mostrarReservas() {
    await cargarReservasDelServidor();
    
    document.getElementById('crear-reserva').style.display = 'none';
    document.getElementById('lista-reservas-section').style.display = 'block';
    document.getElementById('progreso-section').style.display = 'none';
    document.getElementById('historial-section').style.display = 'none';
    
    const ul = document.getElementById('lista-reservas');
    ul.innerHTML = '';
    
    reservas.forEach(r => {
        const li = document.createElement('li');
        li.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px;">
                <span>${r.fecha} ${r.hora} - ${r.actividad} con ${r.entrenador}</span>
                <button onclick="cancelarReserva(${r.id})" style="width: auto; padding: 5px 10px; margin: 0; background: linear-gradient(90deg,#dc3545,#c82333);">
                    Cancelar
                </button>
            </div>
        `;
        ul.appendChild(li);
    });
}

async function verProgreso() {
    document.getElementById('crear-reserva').style.display = 'none';
    document.getElementById('lista-reservas-section').style.display = 'none';
    document.getElementById('progreso-section').style.display = 'block';
    document.getElementById('historial-section').style.display = 'none';
    
    try {
        const response = await fetch(`${API_URL}/progreso/${currentUserId}`);
        const data = await response.json();
        
        document.getElementById('progreso-text').textContent = 
            `Progreso del entrenamiento: ${data.porcentaje}% completado. (${data.completadas}/${data.total} clases)`;
    } catch (error) {
        console.error('Error al cargar progreso:', error);
        document.getElementById('progreso-text').textContent = 
            'Progreso del entrenamiento: 0% completado.';
    }
}

async function cargarHistorialDelServidor() {
    try {
        const response = await fetch(`${API_URL}/historial/${currentUserId}`);
        const data = await response.json();
        historialReservas = data.map(r => ({
            id: r.id,
            actividad: r.actividad,
            fecha: r.fecha,
            hora: r.hora.substring(0, 5),
            entrenador: r.nombre_entrenador,
            estado: r.estado,
            fechaCreacion: new Date(r.fecha_creacion).toLocaleString('es-ES'),
            fechaModificacion: new Date(r.fecha_modificacion).toLocaleString('es-ES')
        }));
    } catch (error) {
        console.error('Error al cargar historial:', error);
        showToast('Error al cargar historial');
    }
}

async function mostrarHistorial() {
    await cargarHistorialDelServidor();
    
    document.getElementById('crear-reserva').style.display = 'none';
    document.getElementById('lista-reservas-section').style.display = 'none';
    document.getElementById('progreso-section').style.display = 'none';
    document.getElementById('historial-section').style.display = 'block';
    
    const ul = document.getElementById('lista-historial');
    ul.innerHTML = '';
    
    if (historialReservas.length === 0) {
        ul.innerHTML = '<li style="text-align: center; color: #666;">No hay reservas en el historial</li>';
        return;
    }
    
    historialReservas.forEach(r => {
        const li = document.createElement('li');
        const estadoColor = r.estado === 'activa' ? '#28a745' : '#dc3545';
        const estadoIcon = r.estado === 'activa' ? '✅' : '❌';
        
        li.innerHTML = `
            <div style="padding: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <strong style="color: ${estadoColor};">${estadoIcon} ${r.estado.toUpperCase()}</strong>
                    <small style="color: #666;">Creada: ${r.fechaCreacion}</small>
                </div>
                <div style="margin-bottom: 5px;">
                    <strong>${r.fecha} ${r.hora}</strong> - ${r.actividad} con ${r.entrenador}
                </div>
                ${r.estado === 'cancelada' ? 
                    `<small style="color: #666;">Cancelada: ${r.fechaModificacion}</small>` : 
                    '<small style="color: #28a745;">Reserva activa</small>'
                }
            </div>
        `;
        ul.appendChild(li);
    });
}

async function reservarClase() {
    const actividad = document.getElementById('actividad').value;
    const fecha = document.getElementById('fecha').value;
    const hora = document.getElementById('hora').value;
    const entrenador = document.getElementById('entrenador').value;

    // Validar que todos los campos estén completos
    if (!actividad) {
        showToast('❌ Por favor selecciona una actividad');
        return;
    }
    if (!fecha) {
        showToast('❌ Por favor selecciona una fecha');
        return;
    }
    if (!hora || hora === '' || hora === 'No hay horas disponibles') {
        showToast('❌ No hay horas disponibles para la combinación seleccionada. Intenta con otra fecha.');
        return;
    }
    if (!entrenador) {
        showToast('❌ Por favor selecciona un entrenador');
        return;
    }

    try {
        console.log('Intentando reservar:', { actividad, fecha, hora, entrenador });
        
        // Buscar el bloque correspondiente en los bloques ya cargados
        const bloqueSeleccionado = bloquesDisponibles.find(b => 
            b.fecha === fecha && 
            b.hora.substring(0, 5) === hora && 
            b.nombre_entrenador === entrenador &&
            b.actividad === actividad
        );

        console.log('Bloque encontrado:', bloqueSeleccionado);

        if (!bloqueSeleccionado) {
            showToast('❌ No se encontró la clase. Por favor intenta con una fecha que tenga clases disponibles (ej: 25-10-2025)');
            return;
        }

        // Guardar datos de la reserva en sessionStorage
        const datosReserva = {
            usuario_id: currentUserId,
            bloque_id: bloqueSeleccionado.id,
            fecha: fecha,
            hora: hora,
            entrenador: entrenador,
            actividad: actividad,
            precio: '$1 CLP'
        };

        console.log('Guardando datos en sessionStorage:', datosReserva);
        sessionStorage.setItem('datosReserva', JSON.stringify(datosReserva));
        console.log('Datos guardados, redirigiendo...');
        
        // Redirigir a la página de confirmación
        window.location.href = '/confirmar-reserva.html';
        console.log('Después de asignar location.href');
        
    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

// === API CANCELACION ===
function validarTiempoCancelacion(fechaReserva, horaReserva) {
    const [year, month, day] = fechaReserva.split('-');
    const [hour, minute] = horaReserva.split(':');
    const fechaHoraReserva = new Date(year, month - 1, day, hour, minute || 0);
    const ahora = new Date();
    const diferenciaHoras = (fechaHoraReserva - ahora) / (1000 * 60 * 60);
    return diferenciaHoras >= 2;
}

// Variable global para almacenar la reserva que se está cancelando
let reservaACancelar = null;

async function cancelarReserva(reservaId) {
    const reserva = reservas.find(r => r.id == reservaId);
    
    if (!reserva) {
        showToast('Error: Reserva no encontrada');
        return;
    }
    
    // Guardar la reserva para usarla en las funciones del modal
    reservaACancelar = reserva;
    
    // Mostrar modal con información de la reserva
    document.getElementById('modal-fecha').textContent = reserva.fecha;
    document.getElementById('modal-hora').textContent = reserva.hora;
    document.getElementById('modal-actividad').textContent = reserva.actividad;
    document.getElementById('modal-entrenador').textContent = reserva.entrenador;
    document.getElementById('modal-cancelacion').style.display = 'block';
}

function cerrarModalCancelacion() {
    document.getElementById('modal-cancelacion').style.display = 'none';
    reservaACancelar = null;
}

async function confirmarReembolso() {
    if (!reservaACancelar) {
        showToast('Error: No hay reserva seleccionada');
        return;
    }
    
    // Validar tiempo de cancelación
    if (!validarTiempoCancelacion(reservaACancelar.fecha, reservaACancelar.hora)) {
        showToast('❌ No se puede obtener reembolso: Debes cancelar con al menos 2 horas de anticipación');
        cerrarModalCancelacion();
        return;
    }

    try {
        const response = await fetch(`${API_URL}/reservas/${reservaACancelar.id}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Reserva cancelada. El reembolso se procesará en 24-48 horas');
            cerrarModalCancelacion();
            await mostrarReservas();
            await cargarHistorialDelServidor();
        } else {
            showToast('❌ Error al cancelar reserva');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

function mostrarReagendar() {
    // Ocultar modal de cancelación y mostrar modal de reagendar
    document.getElementById('modal-cancelacion').style.display = 'none';
    document.getElementById('modal-reagendar').style.display = 'block';
    
    // Configurar valores del modal de reagendar
    const hoy = new Date();
    const hoyStr = hoy.toISOString().split('T')[0];
    document.getElementById('reagendar-fecha').min = hoyStr;
    
    // Preseleccionar la misma actividad
    if (reservaACancelar) {
        document.getElementById('reagendar-actividad').value = reservaACancelar.actividad;
    }
    
    // Configurar el listener para el cambio de fecha
    const fechaInput = document.getElementById('reagendar-fecha');
    fechaInput.addEventListener('change', () => llenarHorasReagendar());
}

function llenarHorasReagendar() {
    const select = document.getElementById('reagendar-hora');
    select.innerHTML = '';
    const fechaSeleccionada = new Date(document.getElementById('reagendar-fecha').value);
    const ahora = new Date();
    const horaActual = ahora.getHours();
    const minutoActual = ahora.getMinutes();

    for (let h = 10; h <= 21; h++) {
        if (fechaSeleccionada.toDateString() === ahora.toDateString()) {
            if (h < horaActual || (h === horaActual && minutoActual > 0)) continue;
        }
        const option = document.createElement('option');
        option.value = `${h}:00`;
        option.textContent = `${h}:00`;
        select.appendChild(option);
    }
}

function volverACancelacion() {
    document.getElementById('modal-reagendar').style.display = 'none';
    document.getElementById('modal-cancelacion').style.display = 'block';
}

async function confirmarReagendar() {
    if (!reservaACancelar) {
        showToast('Error: No hay reserva seleccionada');
        return;
    }
    
    const nuevaActividad = document.getElementById('reagendar-actividad').value;
    const nuevaFecha = document.getElementById('reagendar-fecha').value;
    const nuevaHora = document.getElementById('reagendar-hora').value;
    const nuevoEntrenador = document.getElementById('reagendar-entrenador').value;
    
    if (!nuevaFecha || !nuevaHora) {
        showToast('⚠️ Debes seleccionar fecha y hora');
        return;
    }
    
    try {
        // PRIMERO: Verificar que existe disponibilidad ANTES de cancelar
        const bloquesResponse = await fetch(`${API_URL}/bloques`);
        const bloques = await bloquesResponse.json();
        
        const bloqueNuevo = bloques.find(b => 
            b.actividad === nuevaActividad &&
            b.fecha === nuevaFecha &&
            b.hora.substring(0, 5) === nuevaHora &&
            b.nombre_entrenador === nuevoEntrenador
        );
        
        if (!bloqueNuevo) {
            showToast('❌ No hay cupos disponibles para esa fecha/hora');
            return;
        }
        
        if (bloqueNuevo.cupos_disponibles <= 0) {
            showToast('❌ No quedan cupos disponibles para ese horario');
            return;
        }
        
        // SEGUNDO: Si hay disponibilidad, cancelar la reserva actual
        const deleteResponse = await fetch(`${API_URL}/reservas/${reservaACancelar.id}`, {
            method: 'DELETE'
        });
        
        const deleteData = await deleteResponse.json();
        
        if (!deleteData.success) {
            showToast('❌ Error al cancelar la reserva anterior');
            return;
        }
        
        // TERCERO: Guardar datos en sessionStorage para la nueva reserva
        sessionStorage.setItem('reservaActividad', nuevaActividad);
        sessionStorage.setItem('reservaFecha', nuevaFecha);
        sessionStorage.setItem('reservaHora', nuevaHora);
        sessionStorage.setItem('reservaEntrenador', nuevoEntrenador);
        sessionStorage.setItem('bloque_id', bloqueNuevo.id);
        sessionStorage.setItem('esReagendamiento', 'true'); // Marcar como reagendamiento
        
        // Cerrar modal y redirigir a confirmar-reserva
        document.getElementById('modal-reagendar').style.display = 'none';
        reservaACancelar = null;
        
        showToast('✅ Redirigiendo a confirmar nueva reserva...');
        setTimeout(() => {
            window.location.href = '/confirmar-reserva.html';
        }, 1000);
        
    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

// === ADMIN ===
async function cargarBloquesDelServidor() {
    try {
        const response = await fetch(`${API_URL}/bloques`);
        const data = await response.json();
        bloques = data.map(b => ({
            id: b.id,
            actividad: b.actividad,
            fecha: b.fecha,
            hora: b.hora.substring(0, 5),
            entrenador: b.nombre_entrenador,
            cupos: b.cupos_disponibles
        }));
        mostrarBloques();
    } catch (error) {
        console.error('Error al cargar bloques:', error);
        showToast('Error al cargar bloques');
    }
}

async function crearBloque() {
    const actividad = document.getElementById('act-admin').value;
    const fecha = document.getElementById('fecha-admin').value;
    const hora = document.getElementById('hora-admin').value;
    const entrenador_nombre = document.getElementById('entrenador-admin').value;
    const capacidad_maxima = parseInt(document.getElementById('cupos-admin').value) || 10;

    if (!fecha || !hora || !entrenador_nombre) {
        showToast('⚠️ Completa todos los campos');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/admin/cupos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                fecha,
                hora,
                entrenador_nombre,
                actividad,
                capacidad_maxima
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✅ Cupo creado exitosamente!');
            await cargarBloquesDelServidor();
            // Limpiar formulario
            document.getElementById('fecha-admin').value = '';
            document.getElementById('cupos-admin').value = '10';
        } else {
            showToast(`❌ ${data.error || 'Error al crear cupo'}`);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

function mostrarBloques() {
    const ul = document.getElementById('lista-bloques');
    ul.innerHTML = '';
    bloques.forEach(b => {
        ul.innerHTML += `<li>${b.fecha} ${b.hora} - ${b.actividad} con ${b.entrenador} [Cupos: ${b.cupos}]</li>`;
    });
}

// === ENTRENADOR ===
async function mostrarAlumnosDelServidor(nombreEntrenador) {
    try {
        const response = await fetch(`${API_URL}/entrenador/${encodeURIComponent(nombreEntrenador)}/alumnos`);
        const alumnos = await response.json();
        
        const ul = document.getElementById('lista-alumnos');
        ul.innerHTML = '';
        
        if (alumnos.length === 0) {
            ul.innerHTML = '<li>No tienes alumnos asignados aún</li>';
        } else {
            alumnos.forEach(alumno => {
                ul.innerHTML += `<li>Alumno: ${alumno.username}</li>`;
            });
        }
    } catch (error) {
        console.error('Error al cargar alumnos:', error);
        const ul = document.getElementById('lista-alumnos');
        ul.innerHTML = '<li>Error al cargar alumnos</li>';
    }
}

// === PERFIL DEL CLIENTE ===
function mostrarPerfil() {
    ocultarTodasLasSeccionesCliente();
    document.getElementById('perfil-section').style.display = 'block';
    cargarPerfilDelServidor();
}

async function cargarPerfilDelServidor() {
    try {
        const response = await fetch(`${API_URL}/usuarios/${currentUserId}`);
        const data = await response.json();
        
        if (data.success) {
            const usuario = data.usuario;
            document.getElementById('perfil-email').value = usuario.email || '';
            document.getElementById('perfil-telefono').value = usuario.telefono || '';
            document.getElementById('perfil-direccion').value = usuario.direccion || '';
            document.getElementById('perfil-fechaNac').value = usuario.fecha_nacimiento || '';
            document.getElementById('perfil-peso').value = usuario.peso || '';
            document.getElementById('perfil-altura').value = usuario.altura || '';
            document.getElementById('perfil-objetivo').value = usuario.objetivo || '';
        }
    } catch (error) {
        console.error('Error al cargar perfil:', error);
        showToast('❌ Error al cargar perfil');
    }
}

async function guardarPerfil() {
    const perfil = {
        email: document.getElementById('perfil-email').value,
        telefono: document.getElementById('perfil-telefono').value,
        direccion: document.getElementById('perfil-direccion').value,
        fecha_nacimiento: document.getElementById('perfil-fechaNac').value,
        peso: parseFloat(document.getElementById('perfil-peso').value) || null,
        altura: parseFloat(document.getElementById('perfil-altura').value) || null,
        objetivo: document.getElementById('perfil-objetivo').value
    };
    
    try {
        const response = await fetch(`${API_URL}/usuarios/${currentUserId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(perfil)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('✅ Perfil actualizado correctamente');
        } else {
            showToast('❌ Error al guardar perfil');
        }
    } catch (error) {
        console.error('Error al guardar perfil:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

function ocultarTodasLasSeccionesCliente() {
    document.getElementById('crear-reserva').style.display = 'none';
    document.getElementById('lista-reservas-section').style.display = 'none';
    document.getElementById('progreso-section').style.display = 'none';
    document.getElementById('historial-section').style.display = 'none';
    document.getElementById('perfil-section').style.display = 'none';
}

// === ADMINISTRADOR - ENTRENADORES ===
function mostrarCrearEntrenador() {
    document.getElementById('crear-entrenador-admin').style.display = 'block';
    document.getElementById('crear-bloque').style.display = 'none';
    document.getElementById('lista-bloques').style.display = 'none';
}

function mostrarCrearCupo() {
    document.getElementById('crear-entrenador-admin').style.display = 'none';
    document.getElementById('crear-bloque').style.display = 'block';
    document.getElementById('lista-bloques').style.display = 'none';
}

function mostrarListaBloques() {
    document.getElementById('crear-entrenador-admin').style.display = 'none';
    document.getElementById('crear-bloque').style.display = 'none';
    document.getElementById('lista-bloques').style.display = 'block';
}

async function crearEntrenador() {
    const nombre = document.getElementById('nombre-entrenador').value.trim();
    const especialidad = document.getElementById('especialidad-entrenador').value.trim();
    
    if (!nombre) {
        showToast('⚠️ Ingresa el nombre del entrenador');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/admin/entrenadores`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nombre, especialidad })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showToast('✅ Entrenador creado exitosamente');
            document.getElementById('nombre-entrenador').value = '';
            document.getElementById('especialidad-entrenador').value = '';
            await cargarEntrenadoresParaAdmin();
        } else {
            showToast(`❌ ${data.error || 'Error al crear entrenador'}`);
        }
    } catch (error) {
        console.error('Error al crear entrenador:', error);
        showToast('❌ Error de conexión con el servidor');
    }
}

async function cargarEntrenadoresParaAdmin() {
    try {
        const response = await fetch(`${API_URL}/entrenadores`);
        const entrenadores = await response.json();
        
        const select = document.getElementById('entrenador-admin');
        select.innerHTML = '';
        
        entrenadores.forEach(e => {
            const option = document.createElement('option');
            option.value = e.nombre;
            option.textContent = `${e.nombre}${e.especialidad ? ' - ' + e.especialidad : ''}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error al cargar entrenadores:', error);
    }
}

// === TOASTS ===
function showToast(msg) {
    const toasts = document.getElementById('toasts');
    const div = document.createElement('div');
    div.className = 'toast';
    div.textContent = msg;
    toasts.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

