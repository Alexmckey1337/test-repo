# -*- coding: utf-8
from __future__ import unicode_literals

from decimal import Decimal
from django.db.models.signals import post_save

from apps.partnership.models import Partnership, Deal, ChurchDeal, ChurchPartner


def create_church_partner(sender, **kwargs):
    partnership = kwargs["instance"]
    if kwargs["created"]:
        if partnership.value > Decimal(0):
            deal = ChurchDeal(partnership=partnership, value=partnership.value)
            deal.save()


def create_partnership(sender, **kwargs):
    partnership = kwargs["instance"]
    if kwargs["created"]:
        if partnership.value > Decimal(0):
            deal = Deal(partnership=partnership, value=partnership.value)
            deal.save()


post_save.connect(create_partnership, sender=Partnership)
post_save.connect(create_church_partner, sender=ChurchPartner)
