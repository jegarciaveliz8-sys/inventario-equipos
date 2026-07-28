import uuid
import qrcode
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.urls import reverse
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords


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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    serial = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    estado = FSMField(default='disponible', choices=ESTADOS, protected=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_fin_garantia = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='equipos/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrs/', blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return f"{self.nombre} ({self.serial})"

    def get_public_url(self):
        return reverse('equipo_ficha_publica', kwargs={'uuid': self.uuid})

    def generar_qr(self):
        url = f"https://tusistema.com/equipos/{self.uuid}/"
        qr = qrcode.make(url, box_size=10, border=2)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        filename = f'qr_{self.serial}.png'
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generar_qr()
        super().save(*args, **kwargs)

    @transition(field=estado, source='disponible', target='asignado')
    def asignar(self):
        pass

    @transition(field=estado, source='asignado', target='en_reparacion')
    def reportar_fallo(self):
        pass

    @transition(field=estado, source='en_reparacion', target='disponible')
    def reparar(self):
        pass

    @transition(field=estado, source=['disponible', 'en_reparacion'], target='dado_de_baja')
    def dar_de_baja(self):
        pass


class Cliente(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    dpi = models.CharField(max_length=50, blank=True, verbose_name='DPI/ID')
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre


class Accesorio(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)
    history = HistoricalRecords()

    def __str__(self):
        return self.nombre

    def stock_bajo(self):
        return self.cantidad <= self.stock_minimo


class Asignacion(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='asignaciones')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='asignaciones')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(blank=True, null=True)
    observaciones = models.TextField(blank=True)
    accesorios_entregados = models.ManyToManyField(Accesorio, blank=True)
    activa = models.BooleanField(default=True)
    ultima_revision = models.DateField(blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-fecha_asignacion']
        verbose_name = 'Asignacion'
        verbose_name_plural = 'Asignaciones'

    def __str__(self):
        return f"{self.equipo} -> {self.cliente}"

    def devolver(self):
        self.activa = False
        self.fecha_devolucion = timezone.now()
        self.equipo.estado = 'disponible'
        self.equipo.save()
        self.save()


class CambioReparacion(models.Model):
    TIPOS = [
        ('reparacion', 'Reparacion'),
        ('cambio_pieza', 'Cambio de Pieza'),
        ('actualizacion', 'Actualizacion'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='cambios')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.TextField()
    tecnico = models.CharField(max_length=200, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Cambio/Reparacion'
        verbose_name_plural = 'Cambios y Reparaciones'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.equipo}"


class HojaResponsabilidad(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
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
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Hoja de Responsabilidad'
        verbose_name_plural = 'Hojas de Responsabilidad'

    def __str__(self):
        return f"Hoja {self.id} - {self.asignacion.cliente}"


class Alerta(models.Model):
    TIPOS = [
        ('garantia', 'Garantia por vencer'),
        ('stock', 'Stock bajo'),
        ('revision', 'Revision pendiente'),
        ('general', 'General'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, blank=True, null=True)
    accesorio = models.ForeignKey(Accesorio, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'

    def __str__(self):
        return self.titulo
