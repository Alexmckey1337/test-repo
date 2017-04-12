from rest_framework.permissions import IsAuthenticated, BasePermission

from account.permissions import HasHierarchyLevelMixin


class CanSeeChurches(IsAuthenticated, HasHierarchyLevelMixin):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of churches
        """
        return (
            super(CanSeeChurches, self).has_permission(request, view) and
            request.user.is_staff or self.level_gte(request, 1)
        )


class AccountCanEditChurchBlock(BasePermission):
    def can_edit(self, current_user, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

        - repentance_date
        - spiritual_level
        - church
        - home_group
        """
        return True


class AccountCanSeeChurchBlock(BasePermission):
    def can_see(self, current_user, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see church block
        """
        return True


class CanSeeHomeGroups(CanSeeChurches):
    def has_permission(self, request, view):
        """
        Checking that the ``request.user`` has the right to see list of home groups
        """
        return super(CanSeeHomeGroups, self).has_permission(request, view)


def can_see_churches(request, view=None):
    """
    Checking that the ``request.user`` has the right to see list of churches
    """
    has_perm = CanSeeChurches()
    return has_perm.has_permission(request, view)


def can_see_home_groups(request, view=None):
    """
    Checking that the ``request.user`` has the right to see list of home groups
    """
    has_perm = CanSeeHomeGroups()
    return has_perm.has_permission(request, view)


def can_edit_church_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to edit fields:

    - repentance_date
    - spiritual_level
    - church
    - home_group
    """
    return AccountCanEditChurchBlock().can_edit(current_user, user)


def can_see_church_block(current_user, user):
    """
    Use for ``/account/<user.id>/`` page. Checking that the ``current_user`` has the right to see church block
    """
    return AccountCanSeeChurchBlock().can_see(current_user, user)
