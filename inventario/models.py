import uuid
from django.db import models


def path_firma(instance, filename):
    return f"firmas/{uuid.uuid4()}.png"


def path_pdf(instance, filename):
    return f"hojas/{uuid.uuid4()}.pdf"


class Equipo(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('asignado', 'Asignado'),
        ('en_reparacion', 'En Reparacion'),
        ('dado_de_baja', 'Dado de Baja'),
    ]
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    serial = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='disponible')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    foto = models.ImageField(upload_to='equipos/', blank=True, null=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return f"{self.nombre} ({self.serial})"


class Cliente(models.Model):
    nombre = models.CharField(max_length=200)
    dpi = models.CharField(max_length=50, blank=True, verbose_name='DPI/ID')
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre


class Accesorio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Asignacion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='asignaciones')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='asignaciones')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True)
    accesorios_entregados = models.ManyToManyField(Accesorio, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_asignacion']
        verbose_name = 'Asignacion'
        verbose_name_plural = 'Asignaciones'

    def __str__(self):
        return f"{self.equipo} -> {self.cliente}"


class CambioReparacion(models.Model):
    TIPOS = [
        ('reparacion', 'Reparacion'),
        ('cambio_pieza', 'Cambio de Pieza'),
        ('actualizacion', 'Actualizacion'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='cambios')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    tecnico = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Cambio/Reparacion'
        verbose_name_plural = 'Cambios y Reparaciones'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.equipo}"


class HojaResponsabilidad(models.Model):
    asignacion = models.OneToOneField(Asignacion, on_delete=models.CASCADE, related_name='hoja')
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_firma = models.DateTimeField(blank=True, null=True)
    firmado = models.BooleanField(default=False)
    firma_imagen = models.ImageField(upload_to=path_firma, blank=True, null=True)
    pdf_generado = models.FileField(upload_to=path_pdf, blank=True, null=True)
    condiciones = models.TextField(
        default="El abajo firmante se hace responsable del equipo descrito en esta hoja. "
                "Se compromete a devolverlo en las mismas condiciones en que fue recibido. "
                "En caso de dano o perdida, cubrira el costo de reparacion o reposicion."
    )

    class Meta:
        verbose_name = 'Hoja de Responsabilidad'
        verbose_name_plural = 'Hojas de Responsabilidad'

    def __str__(self):
        return f"Hoja {self.id} - {self.asignacion.cliente}"
