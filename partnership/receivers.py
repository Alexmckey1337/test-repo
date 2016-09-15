from django.db.models.signals import post_save

from partnership.models import Partnership, Deal


def create_partnership(sender, **kwargs):
    partnership = kwargs["instance"]
    if kwargs["created"]:
        deal = Deal(partnership=partnership, value=partnership.value)
        deal.save()


post_save.connect(create_partnership, sender=Partnership)
