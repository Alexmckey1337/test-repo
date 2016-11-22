from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from summit.models import SummitAnket


class IsSummitMember(IsAuthenticated):
    def has_object_permission(self, request, view, summit):
        if not super(IsSummitMember, self).has_object_permission(request, view, summit):
            return False
        if not SummitAnket.objects.filter(user=request.user, summit=summit).exists():
            return False
        return True

    def has_permission(self, request, view):
        return False


class IsConsultantOrHigh(IsSummitMember):
    def has_object_permission(self, request, view, summit):
        return (
            super(IsConsultantOrHigh, self).has_object_permission(request, view, summit) and
            SummitAnket.objects.get(user=request.user, summit=summit).role >= SummitAnket.CONSULTANT
        )


class IsSupervisorOrHigh(IsSummitMember):
    def has_object_permission(self, request, view, summit):
        return (
            super(IsSupervisorOrHigh, self).has_object_permission(request, view, summit) and
            SummitAnket.objects.get(user=request.user, summit=summit).role >= SummitAnket.SUPERVISOR
        )


class IsConsultantReadOnly(IsSummitMember):
    def has_object_permission(self, request, view, summit):
        return (
            super(IsConsultantReadOnly, self).has_object_permission(request, view, summit) and
            SummitAnket.objects.get(user=request.user, summit=summit).role >= SummitAnket.CONSULTANT and
            request.method in SAFE_METHODS
        )


class IsSupervisorOrConsultantReadOnly(IsConsultantReadOnly):
    def has_object_permission(self, request, view, summit):
        return (
            super(IsSupervisorOrConsultantReadOnly, self).has_object_permission(request, view, summit) or
            IsSupervisorOrHigh().has_permission(request, view)
        )
