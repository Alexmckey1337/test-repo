from rest_framework.permissions import BasePermission
from django.conf import settings


class HasAPIAccess(BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        return request.META.get('HTTP_VISITORS_LOCATION_TOKEN', '') == settings.VISITORS_LOCATION_TOKEN


class CanSeeSummitProfiles(BasePermission):
    def has_object_permission(self, request, view, summit):
        """
        Checking that the ``request.user`` has the right to see list of partners
        """
        return can_see_summit_profiles(request.user, summit)


class HasSummitEntryPerm(BasePermission):
    def has_permission(self, request, view):
        return has_summit_entry_perm(request.user)

    def has_object_permission(self, request, view, obj):
        return has_summit_entry_perm(request.user)


def has_summit_entry_perm(user):
    # return user.is_staff
    return True


def can_see_summit(user, summit_id):
    """
    Checking that the ``user`` has the right to see  summit with id = ``summit_id``
    """
    return user.is_summit_consultant_or_high(summit_id) or user.is_staff


def can_download_summit_participant_report(user, summit_id):
    """
    Checking that the ``user`` has the right to download report (pdf) by participant of the summit
    with id = ``summit_id``
    """
    return user.is_summit_consultant_or_high(summit_id) or user.is_staff


def can_see_report_by_bishop_or_high(user, summit_id):
    """
    Checking that the ``user`` has the right to see report by bishops of the summit
    with id = ``summit_id``
    """
    return user.is_summit_consultant_or_high(summit_id) or user.is_staff


def can_see_any_summit(user):
    """
    Checking that the ``user`` has the right to see any of summit
    """
    return user.is_any_summit_consultant_or_high() or user.is_staff


def can_see_summit_type(user, summit_type):
    """
    Checking that the ``user`` has the right to see  summit_type with id = ``summit_type``
    """
    return user.is_summit_type_consultant_or_high(summit_type) or user.is_staff


def can_see_any_summit_type(user):
    return user.is_any_summit_type_consultant_or_high() or user.is_staff


def can_edit_summit_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit summit block
    """
    return True or user.is_staff


def can_see_summit_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see summit block
    """
    return True or user.is_staff


def can_see_any_summit_ticket(user):
    return user.is_any_summit_supervisor_or_high() or user.is_staff


def can_see_summit_ticket(user, summit):
    return user.is_summit_supervisor_or_high(summit) or user.is_staff


def can_see_summit_history_stats(user, summit):
    return user.is_summit_supervisor_or_high(summit) or user.is_staff


def can_see_summit_profiles(user, summit):
    return user.is_summit_consultant_or_high(summit) or user.is_staff


def can_add_user_to_summit(user, summit):
    return user.is_summit_consultant_or_high(summit) or user.is_staff
