from account.abstact_models import UserPermission
from group.permissions import can_see_churches, can_see_home_groups, can_edit_church_block, can_see_church_block


class GroupUserPermission(UserPermission):
    class Meta:
        abstract = True

    def can_see_churches(self):
        """
        Checking that the ``self`` user has the right to see list of churches
        """
        return can_see_churches(self)

    def can_see_home_groups(self):
        """
        Checking that the ``self`` user has the right to see list of home groups
        """
        return can_see_home_groups(self)

    def can_edit_church_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to edit fields of ``user``:

        - repentance_date
        - spiritual_level
        - church
        - home_group
        """
        return can_edit_church_block(self, user)

    def can_see_church_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to see church block of ``user``
        """
        return can_see_church_block(self, user)
