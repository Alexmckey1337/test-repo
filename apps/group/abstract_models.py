from django.db import models
from django.db.models import Subquery
from django.utils.translation import ugettext

from apps.account.signals import obj_edit
from apps.analytics.utils import foreign_key_to_dict
from apps.group.api import permissions
from apps.group.models import Church


class GroupUserPermission(models.Model):
    class Meta:
        abstract = True

    def can_see_churches(self):
        """
        Checking that the ``self`` user has the right to see list of churches
        """
        return permissions.can_see_churches(self)

    def can_see_home_groups(self):
        """
        Checking that the ``self`` user has the right to see list of home groups
        """
        return permissions.can_see_home_groups(self)

    def can_edit_church_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to edit fields of ``user``:

        - repentance_date
        - spiritual_level
        - church
        - home_group
        """
        return permissions.can_edit_church_block(self, user)

    def can_see_church_block(self, user):
        """
        Use for ``/account/<user.id>/`` page. Checking that the ``self`` user has the right
        to see church block of ``user``
        """
        return permissions.can_see_church_block(self, user)

    def can_see_church(self, church):
        """
        Checking that the ``self`` has the right to see ``church``
        """
        return permissions.can_see_church(self, church)

    def can_create_church(self):
        """
        Checking that the ``self`` has the right to create church
        """
        return permissions.can_create_church(self)

    def can_delete_church(self):
        """
        Checking that the ``self`` has the right to delete church
        """
        return permissions.can_delete_church(self)

    def can_edit_church(self, church):
        """
        Checking that the ``self`` has the right to edit ``church``
        """
        return permissions.can_edit_church(self, church)

    def can_add_user_to_church(self, user, church):
        """
        Checking that the ``self`` has the right to add ``user`` to ``church``
        """
        return permissions.can_add_user_to_church(self, user, church)

    def can_del_user_from_church(self, user, church):
        """
        Checking that the ``self`` has the right to remove ``user`` from ``church``
        """
        return permissions.can_del_user_from_church(self, user, church)

    def can_export_churches(self):
        """
        Checking that the ``self`` has the right to export list of churches
        """
        return permissions.can_export_churches(self)

    def can_export_groups_of_church(self, church):
        """
        Checking that the ``self`` has the right to export list of home groups of ``church``
        """
        return permissions.can_export_groups_of_church(self, church)

    def can_export_users_of_church(self, church):
        """
        Checking that the ``self`` has the right to export list of users of ``church``
        """
        return permissions.can_export_users_of_church(self, church)

    def can_see_home_group(self, home_group):
        """
        Checking that the ``self`` has the right to see ``home_group``
        """
        return permissions.can_see_home_group(self, home_group)

    def can_create_home_group(self):
        """
        Checking that the ``self`` has the right to create home group
        """
        return permissions.can_create_home_group(self)

    def can_delete_home_group(self):
        """
        Checking that the ``self`` has the right to delete home group
        """
        return permissions.can_delete_home_group(self)

    def can_edit_home_group(self, home_group):
        """
        Checking that the ``self`` has the right to edit ``home_group``
        """
        return permissions.can_edit_home_group(self, home_group)

    def can_add_user_to_home_group(self, user, home_group):
        """
        Checking that the ``self`` has the right to add ``user`` to ``home_group``
        """
        return permissions.can_add_user_to_home_group(self, user, home_group)

    def can_del_user_from_home_group(self, user, home_group):
        """
        Checking that the ``self`` has the right to remove ``user`` from ``home_group``
        """
        return permissions.can_del_user_from_home_group(self, user, home_group)

    def can_export_home_groups(self):
        """
        Checking that the ``self`` has the right to export list of home groups
        """
        return permissions.can_export_home_groups(self)

    def set_home_group(self, home_group):
        current_church = self.get_church()
        if current_church:
            current_church.del_count_people_cache()
            current_church.del_count_stable_people_cache()
        if home_group:
            home_group.church.del_count_people_cache()
            home_group.church.del_count_stable_people_cache()

        self.cchurch = None
        self.hhome_group = home_group
        self.save()

    def set_church(self, church):
        current_church = self.get_church()
        if current_church:
            current_church.del_count_people_cache()
            current_church.del_count_stable_people_cache()
        if church:
            church.del_count_people_cache()
            church.del_count_stable_people_cache()

        self.hhome_group = None
        self.cchurch = church
        self.save()

    def del_home_group(self):
        home_group = self.hhome_group
        if home_group:
            self.set_church(home_group.church)

    def set_home_group_and_log(self, home_group, editor=None):
        old_dict = {
            'home_group': foreign_key_to_dict(self.hhome_group, ugettext('Home group')),
            'church': foreign_key_to_dict(self.cchurch, ugettext('Church')),
        }
        self.set_home_group(home_group)
        self.refresh_from_db()
        new_dict = {
            'home_group': foreign_key_to_dict(self.hhome_group, ugettext('Home group')),
            'church': foreign_key_to_dict(self.cchurch, ugettext('Church')),
        }
        obj_edit.send(
            sender=self.__class__,
            new_obj=self,
            old_obj_dict=old_dict,
            new_obj_dict=new_dict,
            editor=editor,
            reason={
                'text': ugettext('Change home group')
            }
        )

    def set_church_and_log(self, church, editor=None):
        old_dict = {
            'home_group': foreign_key_to_dict(self.hhome_group, ugettext('Home group')),
            'church': foreign_key_to_dict(self.cchurch, ugettext('Church')),
        }
        self.set_church(church)
        self.refresh_from_db()
        new_dict = {
            'home_group': foreign_key_to_dict(self.hhome_group, ugettext('Home group')),
            'church': foreign_key_to_dict(self.cchurch, ugettext('Church')),
        }
        obj_edit.send(
            sender=self.__class__,
            new_obj=self,
            old_obj_dict=old_dict,
            new_obj_dict=new_dict,
            editor=editor,
            reason={
                'text': ugettext('Change church')
            }
        )

    def del_home_group_and_log(self, editor=None):
        old_dict = {
            'home_group': foreign_key_to_dict(self.hhome_group, ugettext('Home group')),
            'church': foreign_key_to_dict(self.cchurch, ugettext('Church')),
        }
        self.del_home_group()
        self.refresh_from_db()
        new_dict = {
            'home_group': foreign_key_to_dict(self.hhome_group, ugettext('Home group')),
            'church': foreign_key_to_dict(self.cchurch, ugettext('Church')),
        }
        obj_edit.send(
            sender=self.__class__,
            new_obj=self,
            old_obj_dict=old_dict,
            new_obj_dict=new_dict,
            editor=editor,
            reason={
                'text': ugettext('Delete home group')
            }
        )

    # TODO refactoring
    def get_church(self):
        return self.cchurch or self.hhome_group.church if self.hhome_group else None

    # TODO refactoring
    def get_churches(self):
        users = self.__class__.get_tree(self)
        return Church.objects.filter(pastor__in=Subquery(users.values('pk')))
