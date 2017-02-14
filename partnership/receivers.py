# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal
from django.db.models.signals import post_save

from partnership.models import Partnership, Deal


def create_partnership(sender, **kwargs):
    partnership = kwargs["instance"]
    if kwargs["created"]:
        if partnership.value > Decimal(0):
            deal = Deal(partnership=partnership, value=partnership.value)
            deal.save()


post_save.connect(create_partnership, sender=Partnership)
