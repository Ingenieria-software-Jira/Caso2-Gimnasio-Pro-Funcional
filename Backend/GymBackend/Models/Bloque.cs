namespace GymBackend.Models
{
    public class Bloque
    {
        public int Id { get; set; }
        public string Nombre { get; set; } = null!;
        public DateTime HoraInicio { get; set; }
        public DateTime HoraFin { get; set; }
    }
}
