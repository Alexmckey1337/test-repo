from rest_framework.permissions import BasePermission

from common.permissions import can_vo_org_ua_key


class VoCanSeeDepartment(BasePermission):
    def has_permission(self, request, view):
        """
        For vo.org.ua developers. Checking that can see departments
        """
        return can_vo_org_ua_key(request)
