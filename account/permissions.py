from rest_framework.permissions import BasePermission


class CanSeeAccountPage(BasePermission):
    def has_object_permission(self, request, view, user):
        return can_see_account_page(request.user, user)


class CanCreateUser(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to create a new user
        """
        return can_create_user(request.user)


class CanExportUserList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to export list of users
        """
        return can_export_user_list(request.user)


class CanSeeUserList(BasePermission):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of users
        """
        return can_see_user_list(request.user)


def can_see_account_page(current_user, user):
    """
    Checking that the ``current_user`` has the right to see page ``/account/<user.id>/``
    """
    return (
        current_user.is_staff or
        current_user.is_partner_supervisor_or_high or
        user == current_user or
        user.is_descendant_of(current_user) or
        current_user.is_partner_responsible_of(user)
    )


def can_create_user(user):
    """
    Checking that the ``user`` has the right to create a new user
    """
    return (
        user.is_staff or user.is_leader_or_high or
        user.is_partner_supervisor_or_high or
        user.is_any_summit_supervisor_or_high()
    )


def can_export_user_list(user):
    """
    Checking that the ``user`` has the right to export list of users
    """
    return user.is_staff or user.is_pastor_or_high


def can_see_user_list(user):
    """
    Checking that the ``user`` has the right to see list of users
    """
    return user.is_staff or not user.is_leaf()


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
        user.is_descendant_of(current_user)
    )


def can_edit_description_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - description
    """
    return (
        current_user.is_partner_supervisor_or_high or
        current_user.is_any_summit_supervisor_or_high() or
        user.is_descendant_of(current_user)
    )
