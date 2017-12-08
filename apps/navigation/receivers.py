from django.db.models import signals
from django.dispatch import receiver

from apps.navigation.models import ColumnType, Table, Column


@receiver(signals.post_save, sender=ColumnType)
def sync_column(sender, instance, created, **kwargs):
    if created:
        tables = Table.objects.all()
        user_columns = list()
        for table in tables:
            user_columns.append(Column(
                table=table, columnType=instance, number=instance.number, active=instance.active))

        Column.objects.bulk_create(user_columns)


@receiver(signals.post_save, sender=Table)
def sync_table(sender, instance, **kwargs):
    exist_columns = set(instance.columns.values_list('columnType', flat=True))
    user_new_columns = list()
    for column_type in ColumnType.objects.exclude(pk__in=exist_columns):
        user_new_columns.append(Column(
            table=instance, columnType=column_type, number=column_type.number, active=column_type.active))

    Column.objects.bulk_create(user_new_columns)
