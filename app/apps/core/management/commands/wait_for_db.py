import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""
    def handle(self, *args, **options):
        self.stdout.write('waiting for database...')
        connected = False
        while not connected:
            try:
                db_conn = connections['default']
                db_conn.cursor()
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 5 seconds...')
                time.sleep(5)
            else:
                connected = True
                self.stdout.write(self.style.SUCCESS('Database available!'))
