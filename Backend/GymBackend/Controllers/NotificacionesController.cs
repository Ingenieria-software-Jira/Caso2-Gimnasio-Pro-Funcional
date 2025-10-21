using Microsoft.AspNetCore.Mvc;
using GymBackend.Data;
using GymBackend.Models;
using Microsoft.EntityFrameworkCore;

namespace GymBackend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class NotificacionesController : ControllerBase
    {
        private readonly GymContext _context;
        public NotificacionesController(GymContext context) => _context = context;

        [HttpGet]
        public async Task<IActionResult> GetNotificaciones() => Ok(await _context.Notificaciones.ToListAsync());

        [HttpGet("{id}")]
        public async Task<IActionResult> GetNotificacion(int id)
        {
            var noti = await _context.Notificaciones.FindAsync(id);
            if (noti == null) return NotFound();
            return Ok(noti);
        }

        [HttpPost]
        public async Task<IActionResult> CrearNotificacion(Notificacion noti)
        {
            _context.Notificaciones.Add(noti);
            await _context.SaveChangesAsync();
            return CreatedAtAction(nameof(GetNotificacion), new { id = noti.Id }, noti);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> ActualizarNotificacion(int id, Notificacion noti)
        {
            if (id != noti.Id) return BadRequest();
            _context.Entry(noti).State = EntityState.Modified;
            await _context.SaveChangesAsync();
            return NoContent();
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> EliminarNotificacion(int id)
        {
            var noti = await _context.Notificaciones.FindAsync(id);
            if (noti == null) return NotFound();
            _context.Notificaciones.Remove(noti);
            await _context.SaveChangesAsync();
            return NoContent();
        }
    }
}
