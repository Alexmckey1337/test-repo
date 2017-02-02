# -*- coding: utf-8
from __future__ import unicode_literals

from collections import OrderedDict

from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible


def partner_table():
    l = OrderedDict()
    column_types = ColumnType.objects.filter(category__title="partnership").order_by('number')
    for column in column_types.all():
        d = OrderedDict()
        d['get_title'] = column.verbose_title
        d['ordering_title'] = column.ordering_title
        d['number'] = column.number
        d['active'] = column.active
        d['editable'] = column.editable
        l[column.title] = d
    return l


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
            'fullname', 'phone_number', 'repentance_date', 'spiritual_level', 'born_date'])
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


@python_2_unicode_compatible
class Navigation(models.Model):
    title = models.CharField(max_length=30, unique=True)
    url = models.URLField()

    class Meta:
        verbose_name_plural = 'Навигация'
        ordering = ('id',)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Category(models.Model):
    title = models.CharField(max_length=50)
    common = models.BooleanField(default=False)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class ColumnType(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name="columnTypes", blank=True, null=True)
    verbose_title = models.CharField(max_length=100, blank=True)
    ordering_title = models.CharField(max_length=100, blank=True)
    number = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)

    def __str__(self):
        return '{} ({})'.format(self.title, self.category)

    class Meta:
        verbose_name_plural = "Колонки"


@python_2_unicode_compatible
class Table(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='table')
    columnTypes = models.ManyToManyField(ColumnType,
                                         through='Column',
                                         through_fields=('table', 'columnType'),
                                         blank=True,
                                         related_name='tables')

    def __str__(self):
        return self.user.get_full_name()


@python_2_unicode_compatible
class Column(models.Model):
    table = models.ForeignKey(Table, related_name='columns')
    columnType = models.ForeignKey(ColumnType, related_name='columns')
    number = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.columnType.title

    @property
    def editable(self):
        return self.columnType.editable

    class Meta:
        ordering = ['number']
        unique_together = ('table', 'columnType')


@receiver(signals.post_save, sender=ColumnType)
def sync_column(sender, instance, **kwargs):
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
