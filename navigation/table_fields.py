# -*- coding: utf-8
from collections import OrderedDict
from functools import wraps

from django.utils.translation import ugettext_lazy as _

from navigation.models import Table, ColumnType


def check_user_table_exist(func_table):
    @wraps(func_table)
    def wrapper(user, *args, **kwargs):
        if not (hasattr(user, 'table') and isinstance(user.table, Table)):
            return OrderedDict()
        return func_table(user, *args, **kwargs)

    return wrapper


@check_user_table_exist
def group_table(user, category_title=None, prefix_ordering_title=''):
    table_columns = _filter_group_columns(user.table.columns.select_related('columnType'), category_title)

    return _get_result_table(table_columns, prefix_ordering_title)


@check_user_table_exist
def deal_table(user, prefix_ordering_title=''):
    table_columns = _filter_deals_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns, prefix_ordering_title)


@check_user_table_exist
def church_deal_table(user, prefix_ordering_title=''):
    columns = deal_table(user, prefix_ordering_title=prefix_ordering_title)

    for k in columns:
        if columns[k]['ordering_title'] == 'partnership__user__last_name':
            columns[k]['ordering_title'] = 'partnership__church__title'
    return columns


def _filter_deals_columns(table_columns):
    return table_columns.filter(
        columnType__category__title="deal").exclude(columnType__title='done')


@check_user_table_exist
def payment_table(user, prefix_ordering_title=''):
    table_columns = _filter_payment_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns, prefix_ordering_title)


@check_user_table_exist
def meeting_table(user, category_title=None):
    table_columns = _filter_meeting_columns(user.table.columns.select_related('columnType'), category_title)

    return _get_result_table(table_columns)


@check_user_table_exist
def meetings_summary_table(user, category_title=None):
    table_columns = _filter_meetings_summary_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def reports_summary_table(user, category_title=None):
    table_columns = _filter_reports_summary_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def report_payments_table(user):
    table_columns = _filter_report_payments_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def tasks_table(user):
    table_columns = _filter_tasks_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def partnership_summary_table(user, category_title=None):
    table_columns = _filter_partnership_summary_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def user_table(user, prefix_ordering_title=''):
    table_columns = _filter_user_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns, prefix_ordering_title)


@check_user_table_exist
def partner_table(user):
    table_columns = _filter_partner_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def church_partner_table(user):
    table_columns = _filter_partner_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns)


@check_user_table_exist
def summit_table(user, prefix_ordering_title=''):
    table_columns = _filter_summit_columns(user.table.columns.select_related('columnType'))

    return _get_result_table(table_columns, prefix_ordering_title)


def summit_statistics_table():
    result_table = OrderedDict(
        attended={
            'id': 1,
            'title': _('Присутствие'),
            'ordering_title': 'attended',
            'number': 1,
            'active': True,
            'editable': False
        },
        full_name={
            'id': 2,
            'title': _('ФИО'),
            'ordering_title': 'last_name',
            'number': 2,
            'active': True,
            'editable': False
        },
        responsible={
            'id': 3,
            'title': _('Ответственный'),
            'ordering_title': 'responsible',
            'number': 3,
            'active': True,
            'editable': False
        },
        phone_number={
            'id': 5,
            'title': _('Номер телефона'),
            'ordering_title': 'user__phone_number',
            'number': 5,
            'active': True,
            'editable': False
        },
        code={
            'id': 6,
            'title': _('Номер билета'),
            'ordering_title': 'code',
            'number': 6,
            'active': True,
            'editable': False
        },
        department={
            'id': 4,
            'title': _('Отдел'),
            'ordering_title': 'department',
            'number': 4,
            'active': True,
            'editable': False
        },
    )
    return result_table


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


# Helpers


def _get_result_table(columns_qs, prefix_ordering_title=''):
    result_table = OrderedDict()
    for column in columns_qs.order_by('number'):
        result_table[column.columnType.title] = {
            'id': column.id,
            'title': column.columnType.verbose_title,
            'ordering_title': '{}{}'.format(prefix_ordering_title, column.columnType.ordering_title),
            'number': column.number,
            'active': column.active,
            'editable': column.columnType.editable
        }
    return result_table


def _filter_group_columns(table_columns, category_title):
    if category_title in ('churches', 'home_groups'):
        return table_columns.filter(columnType__category__title=category_title)
    elif category_title == 'group_users':
        return table_columns.filter(columnType__title__in=[
            'fullname', 'phone_number', 'repentance_date', 'spiritual_level', 'born_date'])
    else:
        return table_columns.none()


def _filter_meeting_columns(table_columns, category_title):
    if category_title in ('meetings', 'attends', 'church_report'):
        return table_columns.filter(columnType__category__title=category_title)
    return table_columns.none()


def _filter_user_columns(table_columns):
    return table_columns.filter(
        columnType__category__title="Общая информация")


def _filter_summit_columns(table_columns):
    return table_columns.filter(
        columnType__category__title="summit")


def _filter_partner_columns(table_columns):
    return table_columns.filter(
        columnType__category__title="partnership").exclude(
        columnType__title__in=('count', 'result_value'))


def _filter_partnership_summary_columns(table_columns):
    return table_columns.filter(columnType__category__title='partnership_summary')


def _filter_tasks_columns(table_columns):
    return table_columns.filter(columnType__category__title='tasks')


def _filter_report_payments_columns(table_columns):
    return table_columns.filter(columnType__category__title='report_payments')


def _filter_reports_summary_columns(table_columns):
    return table_columns.filter(columnType__category__title='reports_summary')


def _filter_meetings_summary_columns(table_columns):
    return table_columns.filter(columnType__category__title='meetings_summary')


def _filter_payment_columns(table_columns):
    return table_columns.filter(columnType__category__title='payment')
