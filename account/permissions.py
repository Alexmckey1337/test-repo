from rest_framework.permissions import IsAuthenticated

from partnership.permissions import IsDisciplesOf
from summit.permissions import IsSupervisorOrHigh as IsSummitSupervisorOrHigh


class HasHierarchyLevelMixin:
    @staticmethod
    def level_gte(request, level):
        return request.user.hierarchy and request.user.hierarchy.level >= level


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
                           IsAncestorOfPermissionMixin,
                           IsDisciplesOfPermissionMixin):
    def has_permission(self, request, view):
        return (
            request.user.is_staff or
            request.user.is_partner_supervisor_or_high
        )

    def has_object_permission(self, request, view, account):
        return (
            request.user.is_staff or
            request.user.is_partner_supervisor_or_high or
            self._is_ancestor_of(request, view, account, True) or
            self._is_disciples_of(request, view, account)
        )


class CanAccountObjectEdit(IsAuthenticated,
                           IsAncestorOfPermissionMixin):
    def has_object_permission(self, request, view, account):
        return (
            super(CanAccountObjectEdit, self).has_permission(request, view) and
            request.user.is_staff or
            request.user.is_partner_supervisor_or_high or
            self._is_ancestor_of(request, view, account, True)
        )


class CanSeeChurches(IsAuthenticated, HasHierarchyLevelMixin):
    def has_permission(self, request, view):
        return (
            super(CanSeeChurches, self).has_permission(request, view) and
           request.user.is_staff or self.level_gte(request, 1)
        )


class CanCreateUser(IsAuthenticated):
    def has_permission(self, request, view):
        """
        Checking that the current user has the right to create a new user
        """
        return (
            super(CanCreateUser, self).has_permission(request, view) and
            (request.user.is_staff or request.user.is_leader_or_high or
             request.user.is_partner_supervisor_or_high or
             IsSummitSupervisorOrHigh().has_permission(request, view))
        )


class CanExportUserList(IsAuthenticated):
    def has_permission(self, request, view):
        """
        Checking that the current user has the right to export list of users
        """
        return (
            super(CanExportUserList, self).has_permission(request, view) and
            request.user.is_staff or request.user.is_pastor_or_high
        )


class CanSeeUserList(IsAuthenticated):
    def has_permission(self, request, view):
        """
        Checking that the current user has the right to see list of users
        """
        return (
            super(CanSeeUserList, self).has_permission(request, view) and
            request.user.is_staff or request.user.is_leaf_node
        )


CanSeeHomeGroups = CanSeeChurches


def can_see_churches(request, view=None):
    has_perm = CanSeeChurches()
    return has_perm.has_permission(request, view)


def can_see_home_groups(request, view=None):
    has_perm = CanSeeHomeGroups()
    return has_perm.has_permission(request, view)


def can_create_user(request, view=None):
    """
    Checking that the request.user has the right to create a new user
    """
    has_perm = CanCreateUser()
    return has_perm.has_permission(request, view)


def can_export_user_list(request, view=None):
    """
    Checking that the request.user has the right to export list of users
    """
    has_perm = CanExportUserList()
    return has_perm.has_permission(request, view)


def can_see_user_list(request, view=None):
    """
    Checking that the request.user has the right to see list of users
    """
    has_perm = CanSeeUserList()
    return has_perm.has_permission(request, view)
