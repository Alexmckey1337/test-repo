from django.utils.translation import ugettext_lazy as _
from import_export import fields

from account.models import CustomUser
from common.resources import CustomFieldsModelResource
from group.models import Church, HomeGroup
from group.serializers import BASE_GROUP_USER_FIELDS

COMMON_GROUP_RESOURCE_FIELDS = ('title', 'opening_date', 'city', 'address', 'phone_number', 'website')


class ChurchResource(CustomFieldsModelResource):
    """For excel import/export"""

    class Meta:
        model = Church
        fields = COMMON_GROUP_RESOURCE_FIELDS + ('department', 'pastor', 'country', 'is_open')

    def dehydrate_title(self, church):
        return church.get_title

    def dehydrate_department(self, church):
        return str(church.department)

    def dehydrate_pastor(self, church):
        return str(church.pastor)

    def dehydrate_is_open(self, church):
        return _('Yes') if church.is_open else _('No')


class HomeGroupResource(CustomFieldsModelResource):
    """For excel import/export"""

    class Meta:
        model = HomeGroup
        fields = COMMON_GROUP_RESOURCE_FIELDS + ('church', 'leader')

    def dehydrate_title(self, home_group):
        return home_group.get_title

    def dehydrate_church(self, home_group):
        return str(home_group.church)

    def dehydrate_leader(self, home_group):
        return str(home_group.leader)


class GroupUserResource(CustomFieldsModelResource):
    """For excel import/export"""
    fullname = fields.Field()

    class Meta:
        model = CustomUser
        fields = BASE_GROUP_USER_FIELDS + ('fullname',)

    def dehydrate_master(self, user):
        return '%s %s %s' % (user.master.first_name, user.master.last_name, user.master.middle_name)

    def dehydrate_department(self, user):
        return user.department.title if user.department else ''

    def dehydrate_hierarchy(self, user):
        return user.hierarchy.title if user.hierarchy else ''

    def dehydrate_spiritual_level(self, user):
        return user.get_spiritual_level_display()

    def dehydrate_fullname(self, user):
        return user.fullname
