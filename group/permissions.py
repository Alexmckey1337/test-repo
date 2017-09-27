# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework.permissions import BasePermission


class CanCreateChurch(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create church
        """
        return can_create_church(request.user)


class CanExportChurch(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to export church
        """
        return can_export_churches(request.user)


class CanSeeChurch(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see church
        """
        return can_see_churches(request.user)

    def has_object_permission(self, request, view, church):
        """
        Checking that the ``request.user`` has the right to see ``church``
        """
        return can_see_church(request.user, church)


class CanEditChurch(BasePermission):
    def has_object_permission(self, request, view, church):
        """
        Checking that the ``request.user`` has the right to edit ``church``
        """
        return can_edit_church(request.user, church)


class CanCreateHomeGroup(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create home_group
        """
        return can_create_home_group(request.user)


class CanExportHomeGroup(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to export home_group
        """
        return can_export_home_groups(request.user)


class CanSeeHomeGroup(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see home_group
        """
        return can_see_home_groups(request.user)

    def has_object_permission(self, request, view, home_group):
        """
        Checking that the ``request.user`` has the right to see ``home_group``
        """
        return can_see_home_group(request.user, home_group)


class CanEditHomeGroup(BasePermission):
    def has_object_permission(self, request, view, home_group):
        """
        Checking that the ``request.user`` has the right to edit ``home_group``
        """
        return can_edit_home_group(request.user, home_group)


def can_see_churches(user):
    """
    Checking that the ``user`` has the right to see list of churches
    """
    return (
        user.is_main_bishop_or_high or
        user.__class__.get_tree(user).exclude(church__isnull=True).exists() or user.is_staff
    )


def can_see_church(user, church):
    """
    Checking that the ``user`` has the right to see ``church``
    """
    return church.pastor.is_descendant_of(user) or church.pastor == user or user.is_staff


def can_create_church(user):
    """
    Checking that the ``user`` has the right to create church
    """
    return user.is_main_bishop_or_high or user.is_staff


def can_edit_church(user, church):
    """
    Checking that the ``user`` has the right to edit ``church``
    """
    return user.is_main_bishop_or_high or user.is_staff


def can_add_user_to_church(current_user, user, church):
    """
    Checking that the ``current_user`` has the right to add ``user`` to ``church``
    """
    return user.is_descendant_of(current_user) or current_user.is_staff


def can_del_user_from_church(current_user, user, church):
    """
    Checking that the ``current_user`` has the right to remove ``user`` from ``church``
    """
    return user.is_descendant_of(current_user) or current_user.is_staff


def can_export_churches(user):
    """
    Checking that the ``user`` has the right to export list of churches
    """
    return user.__class__.get_tree(user).exclude(church__isnull=True).exists() or user.is_staff


def can_export_groups_of_church(user, church):
    """
    Checking that the ``user`` has the right to export list of home groups of ``church``
    """
    return user.is_main_bishop_or_high or user.is_staff


def can_export_users_of_church(user, church):
    """
    Checking that the ``user`` has the right to export list of users of ``church``
    """
    return user.is_main_bishop_or_high or user.is_staff


def can_see_home_groups(user):
    """
    Checking that the ``user`` has the right to see list of home groups
    """
    return (
        user.is_main_bishop_or_high or
        user.__class__.get_tree(user).exclude(home_group__isnull=True).exists() or user.is_staff
    )


def can_see_home_group(user, home_group):
    """
    Checking that the ``user`` has the right to see ``home_group``
    """
    return home_group.leader.is_descendant_of(user) or user.is_staff


def can_create_home_group(user):
    """
    Checking that the ``user`` has the right to create home group
    """
    return user.is_main_bishop_or_high or user.is_staff


def can_edit_home_group(user, home_group):
    """
    Checking that the ``user`` has the right to edit ``home_group``
    """
    return user.is_main_bishop_or_high or user.is_staff


def can_add_user_to_home_group(current_user, user, home_group):
    """
    Checking that the ``current_user`` has the right to add ``user`` to ``home_group``
    """
    return user.is_descendant_of(current_user) or user.is_staff


def can_del_user_from_home_group(current_user, user, home_group):
    """
    Checking that the ``current_user`` has the right to remove ``user`` from ``home_group``
    """
    return user.is_descendant_of(current_user) or user.is_staff


def can_export_home_groups(user):
    """
    Checking that the ``user`` has the right to export list of home groups
    """
    return user.__class__.get_tree(user).exclude(home_group__isnull=True).exists()


def can_edit_church_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - repentance_date
    - spiritual_level
    - church
    - home_group
    """
    return True


def can_see_church_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see church block
    """
    return True
