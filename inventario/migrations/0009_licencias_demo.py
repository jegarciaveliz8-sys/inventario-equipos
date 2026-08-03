from django.db import migrations
from decimal import Decimal
from datetime import date, timedelta


def crear_licencias_demo(apps, schema_editor):
    Equipo = apps.get_model('inventario', 'Equipo')
    SoftwareLicencia = apps.get_model('inventario', 'SoftwareLicencia')
    Alerta = apps.get_model('inventario', 'Alerta')
    
    equipos = list(Equipo.objects.all())
    if not equipos:
        return
    
    hoy = date.today()
    
    licencias_data = [
        (0, "office", "Microsoft Office 365 Business", "OFF365-XXXX-67890", hoy - timedelta(days=200), hoy + timedelta(days=15), Decimal("1800.00")),
        (1, "antivirus", "Kaspersky Endpoint Security", "KASP-XXXX-11111", hoy - timedelta(days=150), hoy + timedelta(days=45), Decimal("1200.00")),
        (2, "cad", "AutoCAD 2024", "AUTO-XXXX-22222", hoy - timedelta(days=60), hoy + timedelta(days=120), Decimal("8500.00")),
        (3, "otro", "Adobe Creative Cloud", "ADOBE-XXXX-33333", hoy - timedelta(days=180), hoy - timedelta(days=10), Decimal("3200.00")),
        (4, "base_de_datos", "SQL Server 2022 Standard", "SQL-XXXX-44444", hoy - timedelta(days=365), hoy + timedelta(days=200), Decimal("15000.00")),
        (5, "antivirus", "Norton 360 Deluxe", "NORTON-XXXX-55555", hoy - timedelta(days=360), hoy + timedelta(days=5), Decimal("800.00")),
        (6, "os", "Windows Server 2022 Datacenter", "WIN-SRV-66666", hoy - timedelta(days=580), hoy + timedelta(days=150), Decimal("22000.00")),
        (7, "office", "Microsoft Project Professional", "PROJ-XXXX-77777", hoy - timedelta(days=90), hoy + timedelta(days=80), Decimal("3500.00")),
        (8, "cad", "Autodesk Revit 2024", "REVIT-XXXX-88888", hoy - timedelta(days=120), hoy + timedelta(days=110), Decimal("12000.00")),
    ]
    
    creadas = 0
    for eq_idx, tipo, nombre, clave, f_inicio, f_venc, costo in licencias_data:
        equipo = equipos[eq_idx % len(equipos)]
        
        lic, created = SoftwareLicencia.objects.get_or_create(
            equipo=equipo,
            nombre=nombre,
            defaults={
                "tipo": tipo,
                "clave": clave,
                "fecha_inicio": f_inicio,
                "fecha_vencimiento": f_venc,
                "costo": costo,
                "activa": True,
            }
        )
        
        if created:
            creadas += 1
            dias_restantes = (f_venc - hoy).days
            if dias_restantes <= 30:
                Alerta.objects.get_or_create(
                    tipo="licencia",
                    licencia=lic,
                    defaults={
                        "titulo": f"Licencia por vencer: {nombre}",
                        "mensaje": f"La licencia {nombre} de {equipo} vence el {f_venc} ({dias_restantes} dias).",
                        "leida": False,
                    }
                )
    
    print(f"✅ {creadas} licencias de demo creadas.")


def revertir(apps, schema_editor):
    SoftwareLicencia = apps.get_model('inventario', 'SoftwareLicencia')
    SoftwareLicencia.objects.filter(clave__contains="-XXXX-").delete()


class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0008_categoria_ubicacion_alter_alerta_tipo_and_more'),
    ]

    operations = [
        migrations.RunPython(crear_licencias_demo, revertir),
    ]
