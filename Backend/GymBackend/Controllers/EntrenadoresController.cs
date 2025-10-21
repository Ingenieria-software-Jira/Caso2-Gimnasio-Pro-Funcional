using Microsoft.AspNetCore.Mvc;
using GymBackend.Data;
using GymBackend.Models;
using Microsoft.EntityFrameworkCore;

namespace GymBackend.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class EntrenadoresController : ControllerBase
    {
        private readonly GymContext _context;
        public EntrenadoresController(GymContext context) => _context = context;

        [HttpGet]
        public async Task<IActionResult> GetEntrenadores() => Ok(new[] { "Entrenador1", "Entrenador2" });

        [HttpGet("{id}")]
        public async Task<IActionResult> GetEntrenador(int id) => Ok($"Entrenador{id}");
    }
}
