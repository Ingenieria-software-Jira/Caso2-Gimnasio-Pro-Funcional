using System.ComponentModel.DataAnnotations;

namespace GymBackend.Models
{
    public class Reserva
    {
        [Key]
        public int Id { get; set; }
        public int ClienteId { get; set; }
        public int BloqueId { get; set; }
        public string Estado { get; set; } = "pendiente"; // pendiente, pagada, usada, cancelada, reagendada
        public DateTime FechaReserva { get; set; } = DateTime.Now;
    }
}
