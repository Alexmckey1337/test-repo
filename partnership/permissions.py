from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from partnership.models import Partnership


class IsPartnership(IsAuthenticated):
    def has_permission(self, request, view):
        if not super(IsPartnership, self).has_permission(request, view):
            return False
        if not Partnership.objects.filter(user=request.user).exists():
            return False
        return True


class IsManagerOrHigh(IsPartnership):
    def has_permission(self, request, view):
        return (
            super(IsManagerOrHigh, self).has_permission(request, view) and
            request.user.partnership.level < Partnership.PARTNER
        )


class IsSupervisorOrHigh(IsPartnership):
    def has_permission(self, request, view):
        return (
            super(IsSupervisorOrHigh, self).has_permission(request, view) and
            request.user.partnership.level < Partnership.MANAGER
        )


class IsManagerReadOnly(IsPartnership):
    def has_permission(self, request, view):
        return (
            super(IsManagerReadOnly, self).has_permission(request, view) and
            request.user.partnership.level < Partnership.PARTNER and request.method in SAFE_METHODS
        )


class IsSupervisorOrManagerReadOnly(IsManagerReadOnly):
    def has_permission(self, request, view):
        return (
            super(IsSupervisorOrManagerReadOnly, self).has_permission(request, view) or
            IsSupervisorOrHigh().has_permission(request, view)
        )
