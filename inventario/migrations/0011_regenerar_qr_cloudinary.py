from django.db import migrations
import cloudinary
import cloudinary.uploader
import qrcode
from io import BytesIO


def migrar_qr_a_cloudinary(apps, schema_editor):
    Equipo = apps.get_model('inventario', 'Equipo')
    
    for eq in Equipo.objects.all():
        try:
            site_url = "https://inventario-equipos-hkmd.onrender.com"
            url = f"{site_url}/equipos/{eq.uuid}/"
            
            qr = qrcode.make(url, box_size=10, border=2)
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            buffer.seek(0)
            
            result = cloudinary.uploader.upload(
                buffer,
                folder='inventario/qrs',
                public_id=f'qr_{eq.serial or str(eq.uuid)[:8]}',
                overwrite=True,
                resource_type='image'
            )
            
            eq.qr_code = result['public_id']
            eq.save(update_fields=['qr_code'])
            print(f"✅ QR migrado: {eq.nombre}")
        except Exception as e:
            print(f"❌ Error con {eq.nombre}: {e}")


def revertir(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('inventario', '0010_alter_equipo_qr_code_alter_historicalequipo_qr_code'),
    ]

    operations = [
        migrations.RunPython(migrar_qr_a_cloudinary, revertir),
    ]
