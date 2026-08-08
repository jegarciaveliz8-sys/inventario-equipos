import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from inventario.models import Categoria, Ubicacion

categorias = [
    ('Laptop', 'Computadoras portatiles'),
    ('Desktop', 'Computadoras de escritorio'),
    ('Monitor', 'Pantallas y monitores'),
    ('Impresora', 'Impresoras y multifuncionales'),
    ('Servidor', 'Servidores y estaciones de trabajo'),
    ('Tablet', 'Tabletas digitales'),
    ('Celular', 'Telefonos moviles corporativos'),
    ('Periferico', 'Teclados, mouse, webcams, etc.'),
    ('Red', 'Routers, switches, access points'),
    ('Almacenamiento', 'Discos duros, NAS, SSD externos'),
    ('UPS', 'Reguladores y fuentes de poder'),
    ('Otro', 'Otros equipos tecnologicos'),
]

for nombre, desc in categorias:
    obj, created = Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
    if created:
        print(f'  + Categoria creada: {nombre}')
    else:
        print(f'  = Categoria ya existe: {nombre}')

ubicaciones = [
    ('Oficina Principal', 'Edificio central, piso 1', 'Carlos Mendez'),
    ('Sala de Servidores', 'Data center principal', 'Luis Torres'),
    ('Sucursal Norte', 'Zona 18, 12 calle', 'Ana Lopez'),
    ('Sucursal Sur', 'Villa Nueva, km 15', 'Pedro Ruiz'),
    ('Bodega', 'Almacenamiento de equipos', 'Maria Castillo'),
    ('Recepcion', 'Area de entrada principal', 'Jose Martinez'),
    ('Sala de Juntas A', 'Piso 2, ala este', 'Diana Herrera'),
    ('Sala de Juntas B', 'Piso 2, ala oeste', 'Roberto Diaz'),
    ('Area de Desarrollo', 'Piso 3, area de programadores', 'Fernando Paz'),
    ('Soporte Tecnico', 'Piso 1, area de tecnicos', 'Sandra Morales'),
    ('Call Center', 'Piso 1, extension norte', 'Miguel Angel'),
    ('Guardia', 'Puesto de seguridad', 'Seguridad Privada'),
]

for nombre, desc, resp in ubicaciones:
    obj, created = Ubicacion.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc, 'responsable': resp, 'activa': True})
    if created:
        print(f'  + Ubicacion creada: {nombre}')
    else:
        print(f'  = Ubicacion ya existe: {nombre}')

print('\n✅ Datos iniciales creados correctamente.')
