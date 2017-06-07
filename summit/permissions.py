# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission
from django.conf import settings


class HasAPIAccess(BasePermission):
    message = 'Invalid or missing API Key.'

    def has_permission(self, request, view):
        print(request.META)
        return request.META.get('HTTP_VISITORS_LOCATION_TOKEN', '') == settings.VISITORS_LOCATION_TOKEN


class CanSeeSummitProfiles(BasePermission):
    def has_object_permission(self, request, view, summit):
        """
        Checking that the ``request.user`` has the right to see list of partners
        """
        return can_see_summit_profiles(request.user, summit)


def can_see_summit(user, summit_id):
    """
    Checking that the ``user`` has the right to see  summit with id = ``summit_id``
    """
    return user.is_summit_consultant_or_high(summit_id)


def can_download_summit_participant_report(user, summit_id):
    """
    Checking that the ``user`` has the right to see  summit with id = ``summit_id``
    """
    return user.is_summit_consultant_or_high(summit_id)


def can_see_any_summit(user):
    """
    Checking that the ``user`` has the right to see any of summit
    """
    return user.is_any_summit_consultant_or_high()


def can_see_summit_type(user, summit_type):
    """
    Checking that the ``user`` has the right to see  summit_type with id = ``summit_type``
    """
    return user.is_summit_type_consultant_or_high(summit_type)


def can_see_any_summit_type(user):
    return user.is_any_summit_type_consultant_or_high()


def can_edit_summit_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit summit block
    """
    return True


def can_see_summit_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see summit block
    """
    return True


def can_see_any_summit_ticket(user):
    return user.is_any_summit_supervisor_or_high()


def can_see_summit_ticket(user, summit):
    return user.is_summit_supervisor_or_high(summit)


def can_see_summit_profiles(user, summit):
    return user.is_summit_consultant_or_high(summit)


def can_add_user_to_summit(user, summit):
    return user.is_summit_consultant_or_high(summit)
