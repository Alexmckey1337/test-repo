from rest_framework.permissions import IsAuthenticated, IsAdminUser

from partnership.permissions import IsSupervisorOrHigh, IsDisciplesOf


class IsStaffPermissionMixin:
    @staticmethod
    def _is_staff(request, view):
        return IsAdminUser().has_permission(request, view)


class IsPartnerSupervisorPermissionMixin:
    @staticmethod
    def _is_partner_supervisor(request, view):
        return IsSupervisorOrHigh().has_permission(request, view)


class IsDisciplesOfPermissionMixin:
    @staticmethod
    def _is_disciples_of(request, view, account):
        return IsDisciplesOf().has_object_permission(request, view, account)


class IsDescendantOfPermissionMixin:
    @staticmethod
    def _is_descendant_of(request, view, account, include_self=False):
        return IsDescendantOf().has_object_permission(request, view, account, include_self)


class IsDescendantOf(IsAuthenticated):
    def has_object_permission(self, request, view, account, include_self=False):
        return (
            super(IsDescendantOf, self).has_permission(request, view) and
            request.user.is_descendant_of(account, include_self=include_self)
        )


class IsAncestorOfPermissionMixin:
    @staticmethod
    def _is_ancestor_of(request, view, account, include_self=False):
        return IsAncestorOf().has_object_permission(request, view, account, include_self)


class IsAncestorOf(IsAuthenticated):
    def has_object_permission(self, request, view, account, include_self=False):
        return (
            super(IsAncestorOf, self).has_permission(request, view) and
            request.user.is_ancestor_of(account, include_self=include_self)
        )


class CanAccountObjectRead(IsAuthenticated,
                           IsStaffPermissionMixin,
                           IsPartnerSupervisorPermissionMixin,
                           IsAncestorOfPermissionMixin,
                           IsDisciplesOfPermissionMixin):

    def has_permission(self, request, view):
        return (
            self._is_staff(request, view) or
            self._is_partner_supervisor(request, view)
        )

    def has_object_permission(self, request, view, account):
        return (
            self._is_staff(request, view) or
            self._is_partner_supervisor(request, view) or
            self._is_ancestor_of(request, view, account, True) or
            self._is_disciples_of(request, view, account)
        )


class CanAccountObjectEdit(IsAuthenticated,
                           IsStaffPermissionMixin,
                           IsPartnerSupervisorPermissionMixin,
                           IsAncestorOfPermissionMixin):
    def has_object_permission(self, request, view, account):
        return (
            self._is_staff(request, view) or
            self._is_partner_supervisor(request, view) or
            self._is_ancestor_of(request, view, account, True)
        )
