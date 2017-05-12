from django.conf import settings

from account.abstract_models import UserPermission
from summit.models import SummitType
from summit.permissions import can_see_summit, can_see_summit_type, can_see_any_summit, can_see_any_summit_type


class SummitUserPermission(UserPermission):
    class Meta:
        abstract = True

    def can_see_summit(self, summit_id):
        return can_see_summit(self, summit_id)

    def can_see_summit_type(self, summit_type):
        request = self._perm_req()
        return can_see_summit_type(request, summit_type)

    def can_see_any_summit(self):
        return can_see_any_summit(self)

    def can_see_any_summit_type(self):
        request = self._perm_req()
        return can_see_any_summit_type(request)

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
