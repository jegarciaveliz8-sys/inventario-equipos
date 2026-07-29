#!/bin/bash
cd /home/jose/inventario_equipos
source venv/bin/activate
python manage.py backup_db
