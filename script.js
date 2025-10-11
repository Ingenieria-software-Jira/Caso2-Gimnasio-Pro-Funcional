let reservas=[];
let bloques=[];
let historialReservas=[]; // Array para guardar el historial completo de reservas

// === LOGIN ===
function login(){
    const role=document.getElementById('role').value;
    const username=document.getElementById('username').value.trim();
    if(!username){ showToast('Ingresa un usuario'); return; }

    // INICIAR MÚSICA SOLO SI NO ESTABA PAUSADA POR USUARIO
    const audio = document.getElementById('musica');
    if(audio.paused && !audio.dataset.userPaused){
        audio.play().catch(e=>console.log('Interacción requerida para audio'));
    }

    document.getElementById('login-section').style.display='none';

    if(role==='cliente' || role==='admin'){
        document.getElementById(role+'-section').style.display='block';
    } else if(role==='entrenador'){
        document.getElementById('entrenador-section').style.display='block';
        mostrarAlumnos();
    }
}

// BOTON RETROCEDER
function volverLogin(section){
    document.getElementById(section+'-section').style.display='none';
    document.getElementById('login-section').style.display='block';
}

// TOGGLE MUSICA
function toggleMusic(){
    const audio=document.getElementById('musica');
    if(audio.paused){
        audio.play();
        audio.dataset.userPaused = false; // usuario quiere que suene
        showToast('Música reproducida');
    } else {
        audio.pause();
        audio.dataset.userPaused = true; // usuario pausó
        showToast('Música pausada');
    }
}

// === FECHAS Y HORAS ===
const hoy=new Date();
const hoyStr=hoy.toISOString().split('T')[0];
document.getElementById('fecha').min=hoyStr;
document.getElementById('fecha-admin').min=hoyStr;

function llenarHoras(selectId, fechaInputId){
    const select=document.getElementById(selectId);
    select.innerHTML='';
    const fechaSeleccionada=new Date(document.getElementById(fechaInputId).value);
    const ahora=new Date();
    const horaActual=ahora.getHours();
    const minutoActual=ahora.getMinutes();

    for(let h=10; h<=21; h++){
        if(fechaSeleccionada.toDateString()===ahora.toDateString()){
            if(h<horaActual || (h===horaActual && minutoActual>0)) continue;
        }
        const option=document.createElement('option');
        option.value=`${h}:00`;
        option.textContent=`${h}:00`;
        select.appendChild(option);
    }
}

document.getElementById('fecha').addEventListener('change', ()=>llenarHoras('hora','fecha'));
document.getElementById('fecha-admin').addEventListener('change', ()=>llenarHoras('hora-admin','fecha-admin'));

window.addEventListener('load', ()=>{
    document.getElementById('fecha').value=hoyStr;
    document.getElementById('fecha-admin').value=hoyStr;
    llenarHoras('hora','fecha');
    llenarHoras('hora-admin','fecha-admin');
});

// === CLIENTE ===
function mostrarCrearReserva(){
    document.getElementById('crear-reserva').style.display='block';
    document.getElementById('lista-reservas-section').style.display='none';
    document.getElementById('progreso-section').style.display='none';
    document.getElementById('historial-section').style.display='none';
}

function mostrarReservas(){
    document.getElementById('crear-reserva').style.display='none';
    document.getElementById('lista-reservas-section').style.display='block';
    document.getElementById('progreso-section').style.display='none';
    document.getElementById('historial-section').style.display='none';
    const ul=document.getElementById('lista-reservas');
    ul.innerHTML='';
    reservas.forEach(r=>{
        const li = document.createElement('li');
        li.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px;">
                <span>${r.fecha} ${r.hora} - ${r.actividad} con ${r.entrenador}</span>
                <button onclick="cancelarReserva('${r.id}')" style="width: auto; padding: 5px 10px; margin: 0; background: linear-gradient(90deg,#dc3545,#c82333);">
                    Cancelar
                </button>
            </div>
        `;
        ul.appendChild(li);
    });
}

function verProgreso(){
    document.getElementById('crear-reserva').style.display='none';
    document.getElementById('lista-reservas-section').style.display='none';
    document.getElementById('progreso-section').style.display='block';
    document.getElementById('historial-section').style.display='none';
    document.getElementById('progreso-text').textContent='Progreso del entrenamiento: ejemplo 50% completado.';
}

function mostrarHistorial(){
    document.getElementById('crear-reserva').style.display='none';
    document.getElementById('lista-reservas-section').style.display='none';
    document.getElementById('progreso-section').style.display='none';
    document.getElementById('historial-section').style.display='block';
    
    const ul = document.getElementById('lista-historial');
    ul.innerHTML = '';
    
    if (historialReservas.length === 0) {
        ul.innerHTML = '<li style="text-align: center; color: #666;">No hay reservas en el historial</li>';
        return;
    }
    
    // Ordenar por fecha de creación (más recientes primero)
    const historialOrdenado = [...historialReservas].sort((a, b) => 
        new Date(b.fechaCreacion.split(', ')[0].split('/').reverse().join('-')) - 
        new Date(a.fechaCreacion.split(', ')[0].split('/').reverse().join('-'))
    );
    
    historialOrdenado.forEach(r => {
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

function reservarClase(){
    const actividad=document.getElementById('actividad').value;
    const fecha=document.getElementById('fecha').value;
    const hora=document.getElementById('hora').value;
    const entrenador=document.getElementById('entrenador').value;
    
    // Generar ID único para la reserva
    const id = Date.now() + Math.random();
    const fechaCreacion = new Date().toLocaleString('es-ES');

    const reserva = {id, actividad, fecha, hora, entrenador};
    
    // Agregar a reservas activas
    reservas.push(reserva);
    
    // Agregar al historial con estado activo
    historialReservas.push({
        ...reserva,
        estado: 'activa',
        fechaCreacion: fechaCreacion,
        fechaModificacion: fechaCreacion
    });
    
    showToast('Reserva pagada y agendada!');
    mostrarReservas();
}

// === ADMIN ===
function crearBloque(){
    const actividad=document.getElementById('act-admin').value;
    const fecha=document.getElementById('fecha-admin').value;
    const hora=document.getElementById('hora-admin').value;
    const entrenador=document.getElementById('entrenador-admin').value;
    const cupos=document.getElementById('cupos-admin').value;

    bloques.push({actividad, fecha, hora, entrenador, cupos});
    showToast('Bloque creado!');
    mostrarBloques();
}

function mostrarBloques(){
    const ul=document.getElementById('lista-bloques');
    ul.innerHTML='';
    bloques.forEach(b=>{
        ul.innerHTML+=`<li>${b.fecha} ${b.hora} - ${b.actividad} con ${b.entrenador} [Cupos: ${b.cupos}]</li>`;
    });
}

// === ENTRENADOR ===
function mostrarAlumnos(){
    const ul=document.getElementById('lista-alumnos');
    ul.innerHTML='<li>Alumno: Ejemplo 1</li><li>Alumno: Ejemplo 2</li>';
}

// === API CANCELACION ===
function validarTiempoCancelacion(fechaReserva, horaReserva) {
    // Crear objeto Date con la fecha y hora de la reserva
    const [year, month, day] = fechaReserva.split('-');
    const [hour, minute] = horaReserva.split(':');
    const fechaHoraReserva = new Date(year, month - 1, day, hour, minute || 0);
    
    // Obtener fecha y hora actual
    const ahora = new Date();
    
    // Calcular diferencia en horas
    const diferenciaHoras = (fechaHoraReserva - ahora) / (1000 * 60 * 60);
    
    // Debe ser al menos 2 horas antes
    return diferenciaHoras >= 2;
}

function cancelarReserva(reservaId) {
    // Buscar la reserva por ID
    const reserva = reservas.find(r => r.id == reservaId);
    
    if (!reserva) {
        showToast('Error: Reserva no encontrada');
        return;
    }
    
    // Validar reglas de negocio - 2 horas antes
    if (!validarTiempoCancelacion(reserva.fecha, reserva.hora)) {
        showToast('❌ Petición rechazada: No se puede cancelar con menos de 2 horas de anticipación');
        return;
    }
    
    // Eliminar reserva del array de reservas activas
    const index = reservas.findIndex(r => r.id == reservaId);
    if (index > -1) {
        reservas.splice(index, 1);
        
        // Actualizar estado en el historial
        const historialIndex = historialReservas.findIndex(r => r.id == reservaId);
        if (historialIndex > -1) {
            historialReservas[historialIndex].estado = 'cancelada';
            historialReservas[historialIndex].fechaModificacion = new Date().toLocaleString('es-ES');
        }
        
        showToast('✅ Reserva cancelada exitosamente');
        mostrarReservas(); // Actualizar la lista
    }
}

// === TOASTS ===
function showToast(msg){
    const toasts=document.getElementById('toasts');
    const div=document.createElement('div');
    div.className='toast';
    div.textContent=msg;
    toasts.appendChild(div);
    setTimeout(()=>div.remove(),3000);
}
