# -*- coding: utf-8
from django.db import models


class Navigation(models.Model):
    title = models.CharField(max_length=30, unique=True)
    url = models.URLField()

    class Meta:
        verbose_name_plural = u'Навигация'
        ordering = [('id')]
