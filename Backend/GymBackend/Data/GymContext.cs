using Microsoft.EntityFrameworkCore;
using GymBackend.Models;

namespace GymBackend.Data
{
    public class GymContext : DbContext
    {
        public GymContext(DbContextOptions<GymContext> options) : base(options) { }

        public DbSet<Cliente> Clientes { get; set; }
        public DbSet<Bloque> Bloques { get; set; }
        public DbSet<Pago> Pagos { get; set; }
        public DbSet<Notificacion> Notificaciones { get; set; }
    }
}
