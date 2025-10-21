using System.ComponentModel.DataAnnotations;

public class Entrenador
{
    [Key]
    public int Id { get; set; }

    [Required]
    public string Nombre { get; set; }

    public string Especialidad { get; set; }
}
