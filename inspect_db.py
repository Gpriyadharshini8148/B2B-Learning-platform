import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'udemy.settings')
django.setup()

from django.db import connection

def get_columns(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}';")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"{table_name}: {columns}")

get_columns('enrollments_certificate')
get_columns('enrollments_courseprogress')
get_columns('enrollments_lessonprogress')
get_columns('enrollments_enrollment')
get_columns('enrollments_courseassignment')
