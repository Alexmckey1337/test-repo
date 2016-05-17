# -*- coding: utf-8
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from collections import OrderedDict


def partner_table():
    l = OrderedDict()
    column_types = ColumnType.objects.filter(category__title="partnership").order_by('number')
    for column in column_types.all():
        d = OrderedDict()
        d['title'] = column.verbose_title
        d['ordering_title'] = column.ordering_title
        d['number'] = column.number
        d['active'] = column.active
        d['editable'] = column.editable
        l[column.title] = d
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


class Navigation(models.Model):
    title = models.CharField(max_length=30, unique=True)
    url = models.URLField()

    class Meta:
        verbose_name_plural = u'Навигация'
        ordering = [('id')]


class Category(models.Model):
    title = models.CharField(max_length=50)
    common = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title


class ColumnType(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name="columnTypes", blank=True, null=True)
    verbose_title = models.CharField(max_length=100, blank=True, null=True)
    ordering_title = models.CharField(max_length=100, blank=True, null=True)
    number = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    editable = models.BooleanField(default=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Колонки"


class Table(models.Model):
    user = models.OneToOneField('account.CustomUser', related_name='table')
    columnTypes = models.ManyToManyField(ColumnType,
                                     through='Column',
                                     through_fields=('table', 'columnType'),
                                     blank=True,
                                     related_name='tables')

    def __unicode__(self):
        return self.user.get_full_name()


class Column(models.Model):
    table = models.ForeignKey(Table, related_name='columns')
    columnType = models.ForeignKey(ColumnType, related_name='columns')
    number = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.columnType.title

    @property
    def editable(self):
        return self.columnType.editable

    class Meta:
        ordering = ['number']


@receiver(signals.post_save, sender=ColumnType)
def sync_column(sender, instance, **kwargs):
    if instance.category.common:
        tables = Table.objects.all()
        for table in tables:
            column = Column.objects.create(table=table,
                                           columnType=instance,
                                           number=instance.number,
                                           active=instance.active,
                                           editable=instance.editable)
            column.save()


@receiver(signals.post_save, sender=Table)
def sync_table(sender, instance, **kwargs):
    if not instance.columns.all():
        column_types = ColumnType.objects.filter(category__common=True).all()
        for columnType in column_types.all():
            column = Column.objects.create(table=instance,
                                           columnType=columnType,
                                           number=columnType.number,
                                           active=columnType.active,
                                           editable=columnType.editable)
            column.save()

