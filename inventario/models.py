import uuid
import qrcode
import cloudinary
import cloudinary.uploader
from io import BytesIO
from django.db import models
from django.core.files.base import ContentFile
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django_fsm import FSMField, transition
from simple_history.models import HistoricalRecords
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from cloudinary.models import CloudinaryField  # ← AGREGAR ESTA LÍNEA

def path_firma(instance, filename):
    return f"firmas/{uuid.uuid4()}.png"


def path_pdf(instance, filename):
    return f"hojas/{uuid.uuid4()}.pdf"


# ========== NUEVOS MODELOS ==========

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    responsable = models.CharField(max_length=200, blank=True, verbose_name='Responsable')
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Ubicacion'
        verbose_name_plural = 'Ubicaciones'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nombre


class SoftwareLicencia(models.Model):
    TIPOS = [
        ('os', 'Sistema Operativo'),
        ('office', 'Microsoft Office'),
        ('antivirus', 'Antivirus'),
        ('cad', 'Software CAD/Diseño'),
        ('db', 'Base de Datos'),
        ('otro', 'Otro'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    equipo = models.ForeignKey('Equipo', on_delete=models.CASCADE, related_name='licencias')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='otro')
    nombre = models.CharField(max_length=200)
    clave = models.CharField(max_length=500, blank=True, verbose_name='Clave/Licencia')
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activa = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-fecha_vencimiento']
        verbose_name = 'Licencia de Software'
        verbose_name_plural = 'Licencias de Software'

    def __str__(self):
        return f"{self.nombre} - {self.equipo}"

    def dias_para_vencer(self):
        if self.fecha_vencimiento:
            hoy = timezone.now().date()
            return (self.fecha_vencimiento - hoy).days
        return None

    def esta_por_vencer(self):
        dias = self.dias_para_vencer()
        return dias is not None and dias <= 30 and dias >= 0

    def esta_vencida(self):
        dias = self.dias_para_vencer()
        return dias is not None and dias < 0


class MantenimientoPreventivo(models.Model):
    FRECUENCIAS = [
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    equipo = models.ForeignKey('Equipo', on_delete=models.CASCADE, related_name='mantenimientos_preventivos')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    frecuencia = models.CharField(max_length=20, choices=FRECUENCIAS)
    ultima_fecha = models.DateField(blank=True, null=True, verbose_name='Ultima realizacion')
    proxima_fecha = models.DateField(blank=True, null=True, verbose_name='Proximo mantenimiento')
    tecnico = models.CharField(max_length=200, blank=True)
    completado = models.BooleanField(default=False)
    history = HistoricalRecords()

    class Meta:
        ordering = ['proxima_fecha']
        verbose_name = 'Mantenimiento Preventivo'
        verbose_name_plural = 'Mantenimientos Preventivos'

    def __str__(self):
        return f"{self.titulo} - {self.equipo}"

    def calcular_proxima_fecha(self):
        if not self.ultima_fecha:
            return None
        if self.frecuencia == 'semanal':
            return self.ultima_fecha + timedelta(weeks=1)
        elif self.frecuencia == 'mensual':
            return self.ultima_fecha + relativedelta(months=1)
        elif self.frecuencia == 'trimestral':
            return self.ultima_fecha + relativedelta(months=3)
        elif self.frecuencia == 'semestral':
            return self.ultima_fecha + relativedelta(months=6)
        elif self.frecuencia == 'anual':
            return self.ultima_fecha + relativedelta(years=1)
        return None

    def save(self, *args, **kwargs):
        # Solo generar QR si es nuevo o no tiene qr_code
        if not self.pk or not self.qr_code:
            self.generar_qr()
        super().save(*args, **kwargs)
    def esta_vencido(self):
        if self.proxima_fecha:
            return self.proxima_fecha < timezone.now().date()
        return False

    def dias_para_vencer(self):
        if self.proxima_fecha:
            return (self.proxima_fecha - timezone.now().date()).days
        return None


# ========== MODELOS EXISTENTES CORREGIDOS ==========

class Equipo(models.Model):
    ESTADOS = [
        ('disponible', 'Disponible'),
        ('asignado', 'Asignado'),
        ('en_reparacion', 'En Reparacion'),
        ('dado_de_baja', 'Dado de Baja'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipos')
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    serial = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    estado = FSMField(default='disponible', choices=ESTADOS, protected=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='equipos')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_fin_garantia = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='equipos/', blank=True, null=True)
    qr_code = CloudinaryField('qr_code', folder='inventario/qrs', blank=True, null=True)
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
        try:
            relative_url = reverse('equipo_ficha_publica', kwargs={'uuid': self.uuid})
        except:
            relative_url = f"/equipos/{self.uuid}/"
        
        site_url = getattr(settings, 'SITE_URL', '')
        if site_url:
            url = f"{site_url.rstrip('/')}{relative_url}"
        else:
            url = relative_url

        qr = qrcode.make(url, box_size=10, border=2)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Subir a Cloudinary
        result = cloudinary.uploader.upload(
            buffer,
            folder='inventario/qrs',
            public_id=f'qr_{self.serial or str(self.uuid)[:8]}',
            overwrite=True,
            resource_type='image'
        )
        
        # Guardar public_id de Cloudinary
        self.qr_code = result['public_id']
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

    @transition(field=estado, source='asignado', target='disponible')
    def liberar(self):
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
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='asignaciones', verbose_name='Ubicacion fisica')
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
        self.equipo.liberar()
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
        ('licencia', 'Licencia por vencer'),
        ('mantenimiento', 'Mantenimiento preventivo'),
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
    licencia = models.ForeignKey(SoftwareLicencia, on_delete=models.CASCADE, blank=True, null=True)
    mantenimiento = models.ForeignKey(MantenimientoPreventivo, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'

    def __str__(self):
        return self.titulo


class Evidencia(models.Model):
    TIPOS = [
        ('asignacion', 'Entrega/Asignacion'),
        ('devolucion', 'Devolucion'),
        ('reparacion', 'Reparacion'),
        ('mantenimiento', 'Mantenimiento Preventivo'),
        ('general', 'General'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='evidencias')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='general')
    imagen = models.ImageField(upload_to='evidencias/%Y/%m/', blank=True, null=True)
    url_cloudinary = models.URLField(blank=True, null=True, verbose_name='URL en Cloudinary')
    descripcion = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    subido_por = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.equipo}"


class Notificacion(models.Model):
    TIPOS = [
        ('email', 'Email'),
        ('sistema', 'Sistema'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='email')
    destinatario = models.EmailField()
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    enviado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return self.asunto
