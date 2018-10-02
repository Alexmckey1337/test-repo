from django.db import models
from django.utils.translation import ugettext as _


class Table(models.Model):
    title = models.CharField(_('Title'), max_length=255)

    def __str__(self):
        return self.title


class Column(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    table = models.ForeignKey('Table', on_delete=models.CASCADE, related_name='columns', verbose_name=_('Table'))
    ordering_title = models.CharField(_('Ordering title'), max_length=255)
    active = models.BooleanField(_('Active'), default=False)
    editable = models.BooleanField(_('Editable'), default=False)

    def __str__(self):
        return '%s: %s' % (self.table.title, self.title) or 'Column %d' % self.pk
