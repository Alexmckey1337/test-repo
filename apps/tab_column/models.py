from django.db import models
from django.utils.translation import ugettext as _


class Table(models.Model):
    name = models.CharField(_('Name'), unique=True, max_length=255)

    def __str__(self):
        return self.name


class Column(models.Model):
    table = models.ForeignKey('Table', on_delete=models.CASCADE, related_name='columns', verbose_name=_('Table'))
    name = models.CharField(_('Name'), unique=True, max_length=255)

    def __str__(self):
        return '%s: %s' % (self.table.name, self.name) or 'Column %d' % self.pk
