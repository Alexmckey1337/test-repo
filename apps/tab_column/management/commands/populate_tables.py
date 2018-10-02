from django.core.management.base import BaseCommand
from apps.navigation.table_columns import TABLES
from apps.tab_column.models import Table, Column


class Command(BaseCommand):
    help = 'Populate database with provided tables and columns'

    def handle(self, *args, **options):
        errors = 0

        for title, columns in TABLES.items():

            try:
                table = Table.objects.create(title=title)
                table.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(str(e)))
                errors += 1
                continue

            for column, props in columns.items():
                try:
                    col = Column.objects.create(
                        title=props['title'],
                        table=table,
                        ordering_title=props['ordering_title'],
                        active=props['active'],
                        editable=props['editable']
                    )
                    col.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(str(e)))
                    errors += 1
                    continue

        self.stdout.write(self.style.SUCCESS('Successfully populated database (with %d errors)' % errors))