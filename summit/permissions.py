from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from summit.models import SummitAnket


class IsSummitMember(IsAuthenticated):
    def has_object_permission(self, request, view, summit):
        if not super(IsSummitMember, self).has_permission(request, view):
            return False
        if not SummitAnket.objects.filter(user=request.user, summit=summit).exists():
            return False
        return True

    def has_permission(self, request, view):
        if not super(IsSummitMember, self).has_permission(request, view):
            return False
        return SummitAnket.objects.filter(user=request.user).exists()


class IsSummitTypeMember(IsAuthenticated):
    def has_object_permission(self, request, view, summit_type):
        if not super(IsSummitTypeMember, self).has_permission(request, view):
            return False
        if not SummitAnket.objects.filter(user=request.user, summit__type=summit_type).exists():
            return False
        return True

    def has_permission(self, request, view):
        if not super(IsSummitTypeMember, self).has_permission(request, view):
            return False
        return SummitAnket.objects.filter(user=request.user).exists()


class IsConsultantOrHigh(IsSummitMember):
    def has_object_permission(self, request, view, summit):
        return (
            super(IsConsultantOrHigh, self).has_object_permission(request, view, summit) and
            SummitAnket.objects.get(user=request.user, summit=summit).role >= SummitAnket.CONSULTANT
        )

    def has_permission(self, request, view):
        return (
            super(IsConsultantOrHigh, self).has_permission(request, view) and
            SummitAnket.objects.filter(user=request.user, role__gte=SummitAnket.CONSULTANT).exists())


class IsSummitTypeConsultantOrHigh(IsSummitTypeMember):
    def has_object_permission(self, request, view, summit_type):
        if not super(IsSummitTypeConsultantOrHigh, self).has_object_permission(request, view, summit_type):
            return False
        for anket in SummitAnket.objects.filter(user=request.user, summit__type=summit_type):
            if anket.role >= SummitAnket.CONSULTANT:
                return True
        return False

    def has_permission(self, request, view):
        return (
            super(IsSummitTypeConsultantOrHigh, self).has_permission(request, view) and
            SummitAnket.objects.filter(user=request.user, role__gte=SummitAnket.CONSULTANT).exists())


class IsSupervisorOrHigh(IsSummitMember):
    def has_object_permission(self, request, view, summit):
        return (
            super(IsSupervisorOrHigh, self).has_object_permission(request, view, summit) and
            SummitAnket.objects.get(user=request.user, summit=summit).role >= SummitAnket.SUPERVISOR
        )

    def has_permission(self, request, view):
        return (
            super(IsSupervisorOrHigh, self).has_permission(request, view) and
            SummitAnket.objects.filter(user=request.user, role__gte=SummitAnket.SUPERVISOR).exists())


class IsSummitTypeSupervisorOrHigh(IsSummitTypeMember):
    def has_object_permission(self, request, view, summit_type):
        return (
            super(IsSummitTypeSupervisorOrHigh, self).has_object_permission(request, view, summit_type) and
            SummitAnket.objects.get(user=request.user, summit__type=summit_type).role >= SummitAnket.SUPERVISOR
        )

    def has_permission(self, request, view):
        return (
            super(IsSummitTypeSupervisorOrHigh, self).has_permission(request, view) and
            SummitAnket.objects.filter(user=request.user, role__gte=SummitAnket.SUPERVISOR).exists())


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
            IsSupervisorOrHigh().has_object_permission(request, view, summit)
        )


class CanSeeSummitType(IsAuthenticated):
    def has_object_permission(self, request, view, summit_type):
        return (
            super(CanSeeSummitType, self).has_permission(request, view) and
            IsConsultantOrHigh().has_permission(request, view)
        )


def can_see_summit(request, summit_id, view=None):
    return IsConsultantOrHigh().has_object_permission(request, view, summit_id)


def can_see_any_summit(request, view=None):
    return IsConsultantOrHigh().has_permission(request, view)


def can_see_summit_type(request, summit_type, view=None):
    return IsSummitTypeConsultantOrHigh().has_object_permission(request, view, summit_type)


def can_see_any_summit_type(request, view=None):
    return IsSummitTypeConsultantOrHigh().has_permission(request, view)
