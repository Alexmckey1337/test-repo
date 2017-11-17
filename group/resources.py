from django.utils.translation import ugettext_lazy as _
from import_export import fields
from import_export.resources import ModelDeclarativeMetaclass

from account.models import CustomUser
from common.resources import CustomFieldsModelResource
from group.models import Church, HomeGroup
from group.serializers import BASE_GROUP_USER_FIELDS

COMMON_GROUP_RESOURCE_FIELDS = ('opening_date', 'city', 'address', 'phone_number',
                                'website')
CHURCH_MAIN_RESOURCE_FIELDS = COMMON_GROUP_RESOURCE_FIELDS + ('country', 'is_open')
CHURCH_RESOURCE_FIELDS = CHURCH_MAIN_RESOURCE_FIELDS + ('get_title', 'department', 'pastor')


class ChurchMetaclass(ModelDeclarativeMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = super(ChurchMetaclass, mcs).__new__(mcs, name, bases, attrs)

        def create_dehydrate_method(f):
            def dehydrate_method(self, obj):
                church_field = self.get_church_field(obj)
                return getattr(church_field, f)

            return dehydrate_method

        for f in CHURCH_MAIN_RESOURCE_FIELDS:
            setattr(new_class, 'dehydrate_{}'.format(f), create_dehydrate_method(f))
        return new_class


class ChurchResource(CustomFieldsModelResource):
    """For excel import/export"""
    get_title = fields.Field()

    church_field_name = None

    class Meta:
        model = Church
        fields = CHURCH_RESOURCE_FIELDS

    def get_church_field(self, church):
        if self.church_field_name:
            return getattr(church, self.church_field_name)
        return church

    def dehydrate_department(self, church):
        church_field = self.get_church_field(church)
        return str(church_field.department)

    def dehydrate_pastor(self, church):
        church_field = self.get_church_field(church)
        return str(church_field.pastor)

    def dehydrate_get_title(self, church):
        church_field = self.get_church_field(church)
        return str(church_field.title)

    def dehydrate_is_open(self, church):
        church_field = self.get_church_field(church)
        return _('Yes') if church_field.is_open else _('No')


class HomeGroupResource(CustomFieldsModelResource):
    """For excel import/export"""
    get_title = fields.Field(attribute='title')

    class Meta:
        model = HomeGroup
        fields = COMMON_GROUP_RESOURCE_FIELDS + ('church', 'leader')

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
        return '%s %s %s' % (user.master.first_name,
                             user.master.last_name,
                             user.master.middle_name)

    def dehydrate_departments(self, user):
        return ', '.join(user.departments.values_list('title', flat=True))

    def dehydrate_hierarchy(self, user):
        return user.hierarchy.title if user.hierarchy else ''

    def dehydrate_spiritual_level(self, user):
        return user.get_spiritual_level_display()

    def dehydrate_fullname(self, user):
        return user.fullname
