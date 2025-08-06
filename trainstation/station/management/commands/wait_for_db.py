import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Waiting for database...")

        while True:
            try:
                connection = connections["default"]
                cursor = connection.cursor()
                cursor.execute("SELECT 1;")
                break
            except OperationalError as e:
                self.stdout.write(f"Database not ready: {e}")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database is ready!"))
