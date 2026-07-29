from django.core.management.base import BaseCommand
from django.conf import settings
import shutil
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Crea backup de la base de datos SQLite con fecha'

    def handle(self, *args, **kwargs):
        db_path = settings.DATABASES['default']['NAME']
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'db_backup_{timestamp}.sqlite3'
        shutil.copy2(db_path, backup_path)
        self.stdout.write(self.style.SUCCESS(f'Backup creado: {backup_path}'))
