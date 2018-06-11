from rest_framework.permissions import BasePermission

from common.permissions import can_vo_org_ua_key


class VoCanSeeCities(BasePermission):
    def has_permission(self, request, view):
        """
        For vo.org.ua developers. Checking that  can see list of cities
        """
        return can_vo_org_ua_key(request)
