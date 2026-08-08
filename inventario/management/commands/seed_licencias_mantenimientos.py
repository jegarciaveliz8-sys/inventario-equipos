from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import random
from inventario.models import Equipo, SoftwareLicencia, MantenimientoPreventivo, Alerta


class Command(BaseCommand):
    help = 'Crea licencias de software y mantenimientos preventivos automaticamente'

    def handle(self, *args, **kwargs):
        equipos = list(Equipo.objects.all())
        if not equipos:
            self.stdout.write(self.style.ERROR('No hay equipos en la base de datos.'))
            return

        self.stdout.write(self.style.NOTICE(f'Procesando {len(equipos)} equipos...'))

        # ========== LICENCIAS DE SOFTWARE ==========
        licencias_data = [
            ('Windows 11 Pro', 'os', 365),
            ('Microsoft Office 365', 'office', 365),
            ('Kaspersky Endpoint Security', 'antivirus', 365),
            ('AutoCAD 2024', 'cad', 365),
            ('Adobe Creative Cloud', 'otro', 365),
            ('SQL Server 2022', 'db', 730),
            ('VMware Workstation', 'otro', 730),
            ('Norton Antivirus', 'antivirus', 365),
            ('Windows Server 2022', 'os', 730),
            ('Microsoft Project', 'office', 365),
            ('Autodesk Revit', 'cad', 365),
            ('Bitdefender GravityZone', 'antivirus', 365),
        ]

        licencias_creadas = 0
        for equipo in equipos:
            # Cada equipo tiene 1-3 licencias
            num_licencias = random.randint(1, 3)
            for _ in range(num_licencias):
                nombre, tipo, dias_duracion = random.choice(licencias_data)
                
                # 30% de probabilidad de que la licencia este por vencer
                if random.random() < 0.3:
                    fecha_inicio = date.today() - timedelta(days=random.randint(300, 340))
                else:
                    fecha_inicio = date.today() - timedelta(days=random.randint(0, 300))
                
                fecha_venc = fecha_inicio + timedelta(days=dias_duracion)
                clave = f"XXXXX-XXXXX-XXXXX-XXXXX-{random.randint(10000,99999)}"
                costo = Decimal(random.randint(500, 8000))

                obj, created = SoftwareLicencia.objects.get_or_create(
                    equipo=equipo,
                    nombre=nombre,
                    defaults={
                        'tipo': tipo,
                        'clave': clave,
                        'fecha_inicio': fecha_inicio,
                        'fecha_vencimiento': fecha_venc,
                        'costo': costo,
                        'activa': True
                    }
                )
                if created:
                    licencias_creadas += 1

        self.stdout.write(self.style.SUCCESS(f'  + {licencias_creadas} licencias de software creadas'))

        # ========== MANTENIMIENTOS PREVENTIVOS ==========
        mantenimientos_data = [
            ("Limpieza interna y cambio de pasta termica", "trimestral"),
            ("Revision de bateria y calibracion", "semestral"),
            ("Actualizacion de firmware y drivers", "trimestral"),
            ("Limpieza de ventiladores y disipadores", "mensual"),
            ("Revision de cables y conectores", "semestral"),
            ("Escaneo de virus y optimizacion", "mensual"),
            ("Respaldo de datos y verificacion", "semanal"),
            ("Revision de rendimiento y temperatura", "mensual"),
            ("Limpieza de pantalla y teclado", "semanal"),
            ("Revision de garantia y estado fisico", "anual"),
        ]

        tecnicos = ['Luis Torres', 'Sandra Morales', 'Fernando Paz', 'Carlos Mendez', 'Ana Lopez', 'Diana Herrera', 'Pedro Ruiz']

        mantenimientos_creados = 0
        for equipo in equipos:
            # Cada equipo tiene 1-2 mantenimientos
            num_mant = random.randint(1, 2)
            for _ in range(num_mant):
                titulo, frecuencia = random.choice(mantenimientos_data)
                tecnico = random.choice(tecnicos)
                
                # 40% completados, 60% pendientes (algunos vencidos, algunos proximos)
                completado = random.random() < 0.4
                
                if completado:
                    ultima = date.today() - timedelta(days=random.randint(1, 60))
                else:
                    # Algunos vencidos, algunos proximos
                    ultima = date.today() - timedelta(days=random.randint(-30, 90))

                obj, created = MantenimientoPreventivo.objects.get_or_create(
                    equipo=equipo,
                    titulo=titulo,
                    defaults={
                        'descripcion': f"{titulo} programado para el equipo {equipo.nombre}.",
                        'frecuencia': frecuencia,
                        'ultima_fecha': ultima if completado else (ultima if ultima < date.today() else None),
                        'tecnico': tecnico,
                        'completado': completado
                    }
                )
                if created:
                    mantenimientos_creados += 1

        self.stdout.write(self.style.SUCCESS(f'  + {mantenimientos_creados} mantenimientos preventivos creados'))

        # ========== ALERTAS AUTOMATICAS ==========
        hoy = date.today()
        alertas_creadas = 0

        # Alertas de licencias por vencer (30 dias)
        for lic in SoftwareLicencia.objects.filter(activa=True, fecha_vencimiento__lte=hoy+timedelta(days=30), fecha_vencimiento__gte=hoy):
            _, c = Alerta.objects.get_or_create(
                tipo='licencia',
                licencia=lic,
                defaults={
                    'titulo': f'Licencia por vencer: {lic.nombre}',
                    'mensaje': f'La licencia {lic.nombre} del equipo {lic.equipo} vence el {lic.fecha_vencimiento}.'
                }
            )
            if c:
                alertas_creadas += 1

        # Alertas de mantenimientos proximos (7 dias) o vencidos
        for mp in MantenimientoPreventivo.objects.filter(completado=False, proxima_fecha__lte=hoy+timedelta(days=7)):
            _, c = Alerta.objects.get_or_create(
                tipo='mantenimiento',
                mantenimiento=mp,
                defaults={
                    'titulo': f'Mantenimiento: {mp.titulo}',
                    'mensaje': f'El mantenimiento "{mp.titulo}" del equipo {mp.equipo} esta programado para el {mp.proxima_fecha}.'
                }
            )
            if c:
                alertas_creadas += 1

        self.stdout.write(self.style.SUCCESS(f'  + {alertas_creadas} alertas generadas'))

        self.stdout.write(self.style.SUCCESS('\n✅ Datos creados exitosamente!'))
        self.stdout.write(self.style.NOTICE('Recarga el dashboard para ver los cambios.'))
