# -*- coding: utf-8
from __future__ import unicode_literals


def can_see_churches(user):
    """
    Checking that the ``request.user`` has the right to see list of churches
    """
    return user.is_staff or user.is_leader_or_high


def can_see_home_groups(user):
    """
    Checking that the ``request.user`` has the right to see list of home groups
    """
    return user.is_staff or user.is_leader_or_high


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
