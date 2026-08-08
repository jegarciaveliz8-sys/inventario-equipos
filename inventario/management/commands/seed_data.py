from django.core.management.base import BaseCommand
from inventario.models import Categoria, Ubicacion

class Command(BaseCommand):
    help = 'Crea datos iniciales si no existen'

    def handle(self, *args, **kwargs):
        # Categorías
        categorias = [
            'Laptop', 'Desktop', 'Monitor', 'Impresora', 'Servidor',
            'Red', 'Periferico', 'Almacenamiento', 'UPS', 'General',
            'Tablet', 'Smartphone', 'Proyector', 'Escáner', 'Videoconferencia',
        ]
        for nombre in categorias:
            Categoria.objects.get_or_create(nombre=nombre)
        self.stdout.write(self.style.SUCCESS(f'✅ {len(categorias)} categorías listas'))

        # Ubicaciones
        ubicaciones = [
            ('Oficina Principal', 'Oficina central de operaciones', 'Admin'),
            ('Sala de Servidores', 'Servidores y equipos de red', 'Admin Sistemas'),
            ('Bodega', 'Almacenamiento de equipos y repuestos', 'Almacen'),
            ('Recepcion', 'Atención al público', 'Recepcionista'),
            ('Sala de Juntas', 'Reuniones y videoconferencias', 'Coordinador'),
            ('Area de Desarrollo', 'Estaciones de programación', 'Líder Dev'),
            ('Area Contable', 'Contabilidad y finanzas', 'Jefe Contable'),
            ('Sala de Capacitación', 'Capacitaciones y talleres', 'Coordinador de Capacitación'),
            ('Home Office', 'Trabajo remoto', 'N/A'),
        ]
        for nombre, desc, resp in ubicaciones:
            Ubicacion.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'responsable': resp, 'activa': True}
            )
        self.stdout.write(self.style.SUCCESS(f'✅ {len(ubicaciones)} ubicaciones listas'))
