from django.db import models
from django.utils.translation import ugettext_lazy as _


class CustomUserAbstract(models.Model):
    #: Field for name in the native language of the user
    search_name = models.CharField(_('Field for search by name'), max_length=255, blank=True)
    middle_name = models.CharField(_('Middle name'), max_length=40, blank=True)

    city = models.CharField(_('City'), max_length=255, blank=True)
    country = models.CharField(_('Country'), max_length=255, blank=True)

    BABY, JUNIOR, FATHER = 1, 2, 3
    SPIRITUAL_LEVEL_CHOICES = (
        (BABY, _('Baby')),
        (JUNIOR, _('Junior')),
        (FATHER, _('Father')),
    )
    spiritual_level = models.PositiveSmallIntegerField(
        _('Spiritual Level'), choices=SPIRITUAL_LEVEL_CHOICES, default=1)

    class Meta:
        abstract = True
