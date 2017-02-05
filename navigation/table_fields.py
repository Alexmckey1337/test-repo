from collections import OrderedDict

from navigation.models import Table, ColumnType


def group_table(user, category_title):
    result_table = OrderedDict()
    if category_title == 'churches':
        if not (hasattr(user, 'churches') and isinstance(user.table, Table)):
            return result_table
        table_columns = user.table.columns.select_related('columnType').filter(
            columnType__category__title='churches').order_by('number')

    elif category_title == 'home_groups':
        if not (hasattr(user, 'home_groups') and isinstance(user.table, Table)):
            return result_table
        table_columns = user.table.columns.select_related('columnType').filter(
            columnType__category__title='home_groups').order_by('number')

    elif category_title == 'group_users':
        if not (hasattr(user, 'churches') and isinstance(user.table, Table)):
            if not (hasattr(user, 'home_groups') and isinstance(user.table, Table)):
                return result_table
        table_columns = user.table.columns.select_related('columnType').filter(columnType__title__in=[
            'fullname', 'phone_number', 'repentance_date', 'spiritual_level', 'born_date']).order_by('number')
    else:
        return result_table
    for column in table_columns:
        col = OrderedDict()
        col['id'] = column.id
        col['title'] = column.columnType.verbose_title
        col['ordering_title'] = column.columnType.ordering_title
        col['number'] = column.number
        col['active'] = column.active
        col['editable'] = column.columnType.editable
        result_table[column.columnType.title] = col
    return result_table


def user_table(user, prefix_ordering_title=''):
    l = OrderedDict()
    if not (hasattr(user, 'table') and isinstance(user.table, Table)):
        return l
    column_types = user.table.columns.select_related('columnType').filter(
        columnType__category__title="Общая информация").order_by('number')
    for column in column_types:
        d = OrderedDict()
        d['id'] = column.id
        d['title'] = column.columnType.verbose_title
        d['ordering_title'] = '{}{}'.format(prefix_ordering_title, column.columnType.ordering_title)
        d['number'] = column.number
        d['active'] = column.active
        d['editable'] = column.columnType.editable
        l[column.columnType.title] = d
    return l


def user_partner_table(user):
    l = OrderedDict()
    if not (hasattr(user, 'table') and isinstance(user.table, Table)):
        return l
    column_types = user.table.columns.select_related('columnType').filter(
        columnType__category__title="partnership").exclude(
        columnType__title__in=('count', 'result_value')).order_by('number')
    for column in column_types.all():
        d = OrderedDict()
        d['id'] = column.id
        d['title'] = column.columnType.verbose_title
        d['ordering_title'] = column.columnType.ordering_title
        d['number'] = column.number
        d['active'] = column.active
        d['editable'] = column.columnType.editable
        l[column.columnType.title] = d
    return l


def user_summit_table():
    l = OrderedDict()
    d = OrderedDict()
    d['title'] = 'Код'
    d['ordering_title'] = 'code'
    d['number'] = 1
    d['active'] = True
    d['editable'] = False
    l['code'] = d
    d = OrderedDict()
    d['title'] = 'Оплата'
    d['ordering_title'] = 'value'
    d['number'] = 2
    d['active'] = True
    d['editable'] = False
    l['value'] = d
    d = OrderedDict()
    d['title'] = 'Примечание'
    d['ordering_title'] = 'description'
    d['number'] = 3
    d['active'] = True
    d['editable'] = False
    l['description'] = d
    return l


def event_table():
    l = OrderedDict()
    column_types = ColumnType.objects.filter(category__title="events").order_by('number')
    for column in column_types.all():
        d = OrderedDict()
        d['title'] = column.verbose_title
        d['ordering_title'] = column.ordering_title
        d['number'] = column.number
        d['active'] = column.active
        d['editable'] = column.editable
        l[column.title] = d
    return l