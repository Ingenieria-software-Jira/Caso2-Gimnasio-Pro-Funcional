namespace GymBackend.Models
{
    public class Notificacion
    {
        public int Id { get; set; }
        public string Mensaje { get; set; } = null!;
        public DateTime Fecha { get; set; }
    }
}
