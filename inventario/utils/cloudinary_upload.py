import cloudinary
import cloudinary.uploader
from datetime import datetime


def subir_evidencia(archivo, nombre_base="evidencia"):
    nombre_limpio = "".join(c for c in nombre_base if c.isalnum() or c == '-').lower()
    nombre_archivo = f"{nombre_limpio}_{int(datetime.now().timestamp())}"
    
    resultado = cloudinary.uploader.upload(
        archivo,
        folder="inventario/evidencias",
        public_id=nombre_archivo,
        overwrite=False,
        resource_type="image",
        transformation=[
            {"width": 1600, "height": 1200, "crop": "limit"},
            {"quality": "auto", "fetch_format": "auto"}
        ]
    )
    
    return resultado['secure_url']


def subir_qr(archivo, equipo_id):
    nombre = f"qr_{equipo_id}_{int(datetime.now().timestamp())}"
    
    resultado = cloudinary.uploader.upload(
        archivo,
        folder="inventario/qr-codes",
        public_id=nombre,
        resource_type="image"
    )
    
    return resultado['secure_url']


def eliminar_imagen(public_id):
    return cloudinary.uploader.destroy(public_id)
