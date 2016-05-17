from account.models import COMMON
from models import ColumnType


def create():
    for field in COMMON:
        column_type = ColumnType.objects.create(title=field)
        column_type.save()
        print "Created: " + column_type.title
    print "Done"
