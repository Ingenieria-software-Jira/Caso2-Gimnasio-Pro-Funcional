let reservas=[];
let bloques=[];

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
}

function mostrarReservas(){
    document.getElementById('crear-reserva').style.display='none';
    document.getElementById('lista-reservas-section').style.display='block';
    document.getElementById('progreso-section').style.display='none';
    const ul=document.getElementById('lista-reservas');
    ul.innerHTML='';
    reservas.forEach(r=>{
        ul.innerHTML+=`<li>${r.fecha} ${r.hora} - ${r.actividad} con ${r.entrenador}</li>`;
    });
}

function verProgreso(){
    document.getElementById('crear-reserva').style.display='none';
    document.getElementById('lista-reservas-section').style.display='none';
    document.getElementById('progreso-section').style.display='block';
    document.getElementById('progreso-text').textContent='Progreso del entrenamiento: ejemplo 50% completado.';
}

function reservarClase(){
    const actividad=document.getElementById('actividad').value;
    const fecha=document.getElementById('fecha').value;
    const hora=document.getElementById('hora').value;
    const entrenador=document.getElementById('entrenador').value;

    reservas.push({actividad, fecha, hora, entrenador});
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

// === TOASTS ===
function showToast(msg){
    const toasts=document.getElementById('toasts');
    const div=document.createElement('div');
    div.className='toast';
    div.textContent=msg;
    toasts.appendChild(div);
    setTimeout(()=>div.remove(),3000);
}
