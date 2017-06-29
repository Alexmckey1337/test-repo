from django.db import models
from django.utils.translation import ugettext

from account.signals import obj_edit
from analytics.utils import foreign_key_to_dict
from group.permissions import can_see_churches, can_see_home_groups, can_edit_church_block, can_see_church_block


class GroupUserPermission(models.Model):
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

    def set_home_group(self, home_group):
        self.cchurch = None
        self.hhome_group = home_group
        self.save()

    def set_church(self, church):
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
