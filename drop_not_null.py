import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udemy.settings')
django.setup()

from django.db import connection

def drop_not_null():
    with connection.cursor() as cursor:
        try:
            cursor.execute("ALTER TABLE access_auditlog ALTER COLUMN organization_id DROP NOT NULL;")
            print("Successfully dropped NOT NULL constraint on access_auditlog.organization_id.")
        except Exception as e:
            print(f"Error dropping NOT NULL constraint: {e}")

if __name__ == '__main__':
    drop_not_null()
