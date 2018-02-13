# -*- coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from tinymce.models import HTMLField


class ManualCategory(models.Model):
    title = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(verbose_name=_('Position'))

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('position',)

    def __str__(self):
        return '%s' % self.title


class Manual(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey('help.ManualCategory', related_name='manuals',
                                 verbose_name=_('Manual Category'), on_delete=models.PROTECT)
    position = models.PositiveSmallIntegerField(verbose_name=_('Position'))
    content = HTMLField(verbose_name=_('Content'))

    class Meta:
        verbose_name = _('Manual')
        verbose_name_plural = _('Manuals')
        ordering = ('position',)

    def __str__(self):
        return 'Руководство: %s' % self.title

    def get_absolute_url(self):
        return reverse('help:manual_detail', args=(self.id,))
