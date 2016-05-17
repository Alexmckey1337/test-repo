from navigation.models import Table, Column, ColumnType


def destroy():
    columns = Column.objects.all()
    columns.delete()
    return "DELETED"


def create():
    column_types = ColumnType.objects.filter(category__common=True).all()
    tables = Table.objects.all()
    for table in tables.all():
        for columnType in column_types.all():
            column = Column.objects.create(table=table,
                                           columnType=columnType,
                                           number=columnType.number,
                                           active=columnType.active,
                                           editable=columnType.editable)
            column.save()
    return "CREATED"
