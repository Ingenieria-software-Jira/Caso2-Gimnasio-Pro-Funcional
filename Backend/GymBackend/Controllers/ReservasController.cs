using Microsoft.AspNetCore.Mvc;
using GymBackend.Data;
using GymBackend.Models;
using Microsoft.EntityFrameworkCore;

namespace GymBackend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ReservasController : ControllerBase
    {
        private readonly GymContext _context;
        public ReservasController(GymContext context) => _context = context;

        // Para simplificar, asumimos que se reserva un Bloque por Cliente
        [HttpGet]
        public async Task<IActionResult> GetReservas() => Ok(await _context.Bloques.Include(b => b.Id).ToListAsync());

        // Puedes personalizar GET por id según tu lógica de reservas
    }
}
