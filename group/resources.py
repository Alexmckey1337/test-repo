from django.utils.translation import ugettext_lazy as _

from common.resources import CustomFieldsModelResource
from group.models import Church, HomeGroup

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
