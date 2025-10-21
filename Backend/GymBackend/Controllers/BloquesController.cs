using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using GymBackend.Data;
using GymBackend.Models;

namespace GymBackend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class BloquesController : ControllerBase
    {
        private readonly GymContext _context;
        public BloquesController(GymContext context) { _context = context; }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<Bloque>>> GetBloques()
        {
            return await _context.Bloques.ToListAsync();
        }

        [HttpPost("crear")]
        public async Task<ActionResult<Bloque>> Crear([FromBody] Bloque bloque)
        {
            _context.Bloques.Add(bloque);
            await _context.SaveChangesAsync();
            return Ok(bloque);
        }
    }
}
