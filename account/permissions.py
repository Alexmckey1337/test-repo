from rest_framework.compat import is_authenticated
from rest_framework.permissions import BasePermission

from common.permissions import BaseUserPermission


class CanSeeAccountPage(BasePermission):
    def has_object_permission(self, request, view, user):
        return can_see_account_page(request.user, user)


class CanCreateUser(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create a new user
        """
        return CreateUserPermission(request.user).has_permission()


class CanExportUserList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to export list of users
        """
        return ExportUserListPermission(request.user).has_permission()


class CanSeeUserList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of users
        """
        return SeeUserListPermission(request.user).has_permission()


def can_see_account_page(current_user, user):
    """
    Checking that the ``current_user`` has the right to see page ``/account/<user.id>/``
    """
    return (
        current_user.is_staff or
        current_user.is_partner_supervisor_or_high or
        current_user.is_ancestor_of(user, include_self=True) or
        current_user.is_partner_responsible_of(user)
    )


class CreateUserPermission(BaseUserPermission):
    def has_permission(self):
        """
        Checking that the ``user`` has the right to create a new user
        """
        return (
             self.user.is_staff or self.user.is_leader_or_high or
             self.user.is_partner_supervisor_or_high or
             self.user.is_any_summit_supervisor_or_high()
        )


class SeeUserListPermission(BaseUserPermission):
    def has_permission(self):
        """
        Checking that the ``user`` has the right to see list of users
        """
        return not self.user.is_leaf_node or self.user.is_staff

    def get_queryset(self):
        """
        User-accessible list of users
        """
        queryset = super(SeeUserListPermission, self).get_queryset()

        return queryset.for_user(self.user)


class ExportUserListPermission(SeeUserListPermission):
    def has_permission(self):
        """
        Checking that the ``user`` has the right to export list of users
        """
        return self.user.is_staff or self.user.is_pastor_or_high


class EditUserPermission(BaseUserPermission):
    def has_permission(self):
        """
        Checking that the ``user`` has the right to edit users
        """
        return not self.user.is_leaf_node or self.user.is_staff

    def get_queryset(self):
        """
        User-accessible list of users for edit
        """
        queryset = super(EditUserPermission, self).get_queryset()

        if not is_authenticated(self.user):
            return queryset.none()
        if self.user.is_staff:
            return queryset
        if not self.user.hierarchy:
            return queryset.none()
        return queryset


# Account page: ``/account/<user_id>/``


def can_edit_status_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - department
    - status
    - master
    - divisions
    """
    return (
        current_user.is_partner_supervisor_or_high or
        current_user.is_any_summit_supervisor_or_high() or
        current_user.is_ancestor_of(user)
    )


def can_edit_description_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - description
    """
    return (
        current_user.is_partner_supervisor_or_high or
        current_user.is_any_summit_supervisor_or_high() or
        current_user.is_ancestor_of(user)
    )
