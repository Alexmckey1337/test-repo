# -*- coding: utf-8
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


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
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="columnTypes", blank=True, null=True)
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
    user = models.OneToOneField('account.CustomUser', on_delete=models.CASCADE, related_name='table')
    columnTypes = models.ManyToManyField(ColumnType,
                                         through='Column',
                                         through_fields=('table', 'columnType'),
                                         blank=True,
                                         related_name='tables')

    def __str__(self):
        return self.user.get_full_name()


@python_2_unicode_compatible
class Column(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='columns')
    columnType = models.ForeignKey(ColumnType, on_delete=models.CASCADE, related_name='columns')
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
