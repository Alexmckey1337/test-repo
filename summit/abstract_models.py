from django.conf import settings
from django.db import models

from summit.models import SummitType
from summit.permissions import can_see_summit, can_see_summit_type, can_see_any_summit, can_see_any_summit_type, \
    can_edit_summit_block, can_see_summit_block, can_see_any_summit_ticket, can_see_summit_ticket, \
    can_see_summit_profiles, can_add_user_to_summit


class SummitUserPermission(models.Model):
    class Meta:
        abstract = True

    def can_see_summit(self, summit_id):
        return can_see_summit(self, summit_id)

    def can_see_summit_type(self, summit_type):
        return can_see_summit_type(self, summit_type)

    def can_see_any_summit(self):
        return can_see_any_summit(self)

    def can_see_any_summit_type(self):
        return can_see_any_summit_type(self)

    def can_edit_summit_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to edit summit block of ``user``
        """
        return can_edit_summit_block(self, user)

    def can_see_summit_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to see summit block of ``user``
        """
        return can_see_summit_block(self, user)

    def can_see_any_summit_ticket(self):
        return can_see_any_summit_ticket(self)

    def can_see_summit_ticket(self, summit):
        return can_see_summit_ticket(self, summit)

    def can_see_summit_profiles(self, summit):
        return can_see_summit_profiles(self, summit)

    def can_add_user_to_summit(self, summit):
        return can_add_user_to_summit(self, summit)

    def available_summit_types(self):
        return SummitType.objects.filter(
            summits__ankets__user=self,
            summits__ankets__role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).distinct()

    def is_any_summit_supervisor_or_high(self):
        """
        Checking that the user is supervisor (or higher) of at least one summit
        """
        return self.summit_ankets.filter(role__gte=settings.SUMMIT_ANKET_ROLES['supervisor']).exists()

    def is_summit_supervisor_or_high(self, summit):
        """
        Checking that the user is supervisor (or higher) of summit
        """
        return self.summit_ankets.filter(summit=summit, role__gte=settings.SUMMIT_ANKET_ROLES['supervisor']).exists()

    def is_any_summit_consultant_or_high(self):
        """
        Checking that the user is consultant (or higher) of at least one summit
        """
        return self.summit_ankets.filter(role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).exists()

    def is_summit_consultant_or_high(self, summit):
        """
        Checking that the user is consultant (or higher) of summit
        """
        return self.summit_ankets.filter(summit=summit, role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).exists()

    def is_any_summit_visitor_or_high(self):
        """
        Checking that the user is visitor (or higher) of at least one summit
        """
        return self.summit_ankets.filter(role__gte=settings.SUMMIT_ANKET_ROLES['visitor']).exists()

    def is_summit_visitor_or_high(self, summit):
        """
        Checking that the user is visitor (or higher) of summit
        """
        return self.summit_ankets.filter(summit=summit, role__gte=settings.SUMMIT_ANKET_ROLES['visitor']).exists()

    def is_any_summit_type_supervisor_or_high(self):
        """
        Checking that the user is supervisor (or higher) of at least one summit
        """
        return self.is_any_summit_supervisor_or_high()

    def is_summit_type_supervisor_or_high(self, summit_type):
        """
        Checking that the user is supervisor (or higher) of summit
        """
        return self.summit_ankets.filter(
            summit__type=summit_type, role__gte=settings.SUMMIT_ANKET_ROLES['supervisor']).exists()

    def is_any_summit_type_consultant_or_high(self):
        """
        Checking that the user is consultant (or higher) of at least one summit
        """
        return self.is_any_summit_consultant_or_high()

    def is_summit_type_consultant_or_high(self, summit_type):
        """
        Checking that the user is consultant (or higher) of summit
        """
        return self.summit_ankets.filter(
            summit__type=summit_type, role__gte=settings.SUMMIT_ANKET_ROLES['consultant']).exists()

    def is_any_summit_type_visitor_or_high(self):
        """
        Checking that the user is visitor (or higher) of at least one summit
        """
        return self.is_any_summit_visitor_or_high()

    def is_summit_type_visitor_or_high(self, summit_type):
        """
        Checking that the user is visitor (or higher) of summit
        """
        return self.summit_ankets.filter(
            summit__type=summit_type, role__gte=settings.SUMMIT_ANKET_ROLES['visitor']).exists()
