from django.utils.translation import ugettext as _
from rest_framework import serializers

from apps.account.api.serializers import DepartmentTitleSerializer
from apps.account.models import CustomUser
from apps.event.models import ChurchReport
from apps.group.models import Church, HomeGroup, Direction
from apps.location.api.serializers import CityReadSerializer
from apps.location.models import City
from common.fields import ReadOnlyChoiceField

BASE_GROUP_USER_FIELDS = ('fullname', 'phone_number', 'repentance_date', 'spiritual_level',
                          'born_date')


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'fullname',)


class UserNameWithLinkSerializer(UserNameSerializer):
    class Meta(UserNameSerializer.Meta):
        fields = UserNameSerializer.Meta.fields + ('link',)


class ChurchNameSerializer(serializers.ModelSerializer):
    # title = serializers.CharField(source='get_title', read_only=True)

    class Meta:
        model = Church
        fields = ('id', 'title',)


class HomeGroupNameSerializer(serializers.ModelSerializer):
    # title = serializers.CharField(source='get_title', read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'title', 'church')


class HomeGroupLeaderRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Данный пользователь "{pk_value}" - '
                            'не может быть назначен лидером Домашней Группы.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.')
    }


class HomeGroupSerializer(serializers.ModelSerializer):
    leader = HomeGroupLeaderRelatedField(queryset=CustomUser.objects.filter(
        hierarchy__level__gt=0))
    department = serializers.CharField(source='church.department.id', read_only=True, allow_null=True)
    count_users = serializers.IntegerField(read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'link', 'opening_date', 'title', 'city', 'department',
                  'church', 'leader', 'address', 'phone_number', 'get_title',
                  'website', 'count_users', 'image', 'locality', 'latitude', 'longitude',)


class HomeGroupListSerializer(HomeGroupSerializer):
    church = ChurchNameSerializer()
    leader = UserNameSerializer()
    locality = CityReadSerializer()


class HomeGroupLocationSerializer(serializers.ModelSerializer):
    leader = UserNameSerializer()
    church = ChurchNameSerializer()
    count_users = serializers.IntegerField(read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'title', 'leader', 'church', 'count_users', 'latitude', 'longitude')


class HomeGroupReadSerializer(HomeGroupListSerializer):
    pass


class GroupUserSerializer(serializers.ModelSerializer):
    spiritual_level = ReadOnlyChoiceField(
        choices=CustomUser.SPIRITUAL_LEVEL_CHOICES, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'link',) + BASE_GROUP_USER_FIELDS


class HomeGroupDetailSerializer(serializers.ModelSerializer):
    uusers = GroupUserSerializer(many=True, read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'uusers')


class ChurchPastorRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Данный пользователь "{pk_value}" - '
                            'не может быть назначен пастором Церкви.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.')
    }


class ChurchSerializer(serializers.ModelSerializer):
    link = serializers.CharField(read_only=True)
    pastor = ChurchPastorRelatedField(queryset=CustomUser.objects.filter(
        hierarchy__level__gte=2))

    class Meta:
        model = Church
        fields = ('id', 'opening_date', 'is_open', 'link', 'title', 'get_title',
                  'department', 'pastor', 'country', 'city', 'address', 'website',
                  'phone_number', 'report_currency', 'image', 'region', 'stable_count',
                  'count_people', 'count_home_groups', 'locality', 'latitude', 'longitude',)

    def update(self, instance, validated_data):
        report_currency = validated_data.get('report_currency')
        pastor = validated_data.get('pastor')
        reports = ChurchReport.objects.filter(church_id=instance.id, status__in=[ChurchReport.IN_PROGRESS,
                                                                                 ChurchReport.EXPIRED])

        if report_currency:
            reports.update(currency=report_currency)
        if pastor:
            reports.update(pastor=pastor)

        return super(ChurchSerializer, self).update(instance, validated_data)


class ChurchReadSerializer(ChurchSerializer):
    locality = CityReadSerializer()


class BaseChurchListSerializer(ChurchSerializer):
    department = DepartmentTitleSerializer()
    pastor = UserNameSerializer()
    locality = CityReadSerializer()

    class Meta:
        model = Church
        fields = ('id', 'opening_date', 'is_open', 'link', 'title', 'get_title',
                  'department', 'pastor', 'country', 'city', 'address', 'website',
                  'phone_number', 'report_currency', 'region', 'locality', 'latitude', 'longitude',)


class ChurchTableSerializer(BaseChurchListSerializer):
    class Meta:
        model = Church
        required_fields = ['id', 'link']
        fields = ('id', 'opening_date', 'is_open', 'link', 'title', 'get_title',
                  'department', 'pastor', 'country', 'city', 'address', 'website',
                  'phone_number', 'report_currency', 'region', 'stable_count', 'count_hg_people',
                  'count_people', 'count_home_groups', 'locality', 'latitude', 'longitude',)

    def get_field_names(self, declared_fields, info):
        fields = getattr(self.Meta, 'fields', None)
        if self.context.get('request') is not None:
            columns = self.context.get('columns', [])
            return (self.Meta.required_fields +
                    [i for i in columns.keys() if columns[i]['active']] +
                    list(self._context.get('extra_fields', [])))
        return fields


class ChurchLocationSerializer(serializers.ModelSerializer):
    pastor = UserNameSerializer()

    class Meta:
        model = Church
        fields = ('id', 'title', 'pastor', 'count_people', 'count_home_groups', 'latitude', 'longitude')


class ChurchWithoutPaginationSerializer(serializers.ModelSerializer):
    get_title = serializers.CharField(read_only=True)

    class Meta:
        model = Church
        fields = ('id', 'get_title')


class ChurchStatsSerializer(serializers.ModelSerializer):
    church_users = serializers.IntegerField()
    church_all_users = serializers.IntegerField()
    parishioners_count = serializers.IntegerField()
    leaders_count = serializers.IntegerField()
    home_groups_count = serializers.IntegerField()
    fathers_count = serializers.IntegerField()
    juniors_count = serializers.IntegerField()
    babies_count = serializers.IntegerField()
    partners_count = serializers.IntegerField()

    class Meta:
        model = Church
        fields = ('church_users', 'church_all_users', 'parishioners_count', 'leaders_count',
                  'leaders_count', 'home_groups_count', 'fathers_count', 'juniors_count',
                  'babies_count', 'partners_count')


class HomeGroupStatsSerializer(serializers.ModelSerializer):
    users_count = serializers.IntegerField()
    fathers_count = serializers.IntegerField()
    juniors_count = serializers.IntegerField()
    babies_count = serializers.IntegerField()
    partners_count = serializers.IntegerField()

    class Meta:
        model = HomeGroup
        fields = ('users_count', 'fathers_count', 'juniors_count', 'babies_count',
                  'partners_count')


class AllHomeGroupsListSerializer(serializers.ModelSerializer):
    get_title = serializers.CharField(read_only=True)

    class Meta:
        model = HomeGroup
        fields = ('id', 'get_title')


class ChurchDashboardSerializer(serializers.ModelSerializer):
    churches_count = serializers.IntegerField()
    peoples_in_churches = serializers.IntegerField()
    home_groups_count = serializers.IntegerField()
    peoples_in_home_groups = serializers.IntegerField()

    class Meta:
        model = Church
        fields = ('churches_count', 'peoples_in_churches', 'home_groups_count', 'peoples_in_home_groups')
        read_only_fields = ['__all__']


# tmp


class VoCityReadSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source='name', read_only=True)
    country = serializers.CharField(source='country_name', read_only=True)

    class Meta:
        model = City
        fields = ('id', 'city', 'country')
        read_only_fields = ('city', 'country')


class VoUserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'last_name', 'first_name', 'middle_name')


class VoDirectionSerializer(serializers.ModelSerializer):
    title_by_languages = serializers.DictField()

    class Meta:
        model = Direction
        fields = ('code', 'title_by_languages')


class VoHGSerializer(serializers.ModelSerializer):
    leader = VoUserNameSerializer()
    locality = VoCityReadSerializer()
    count_users = serializers.IntegerField(read_only=True)
    directions = VoDirectionSerializer(many=True, read_only=True)

    class Meta:
        model = HomeGroup
        fields = (
            'id', 'title', 'leader', 'count_users', 'locality',
            'language',
            'directions',  # направленность
        )

    def get_field_names(self, declared_fields, info):
        fields = getattr(self.Meta, 'fields', None)
        only_fields = self.context.get('only_fields', [])
        if only_fields:
            return tuple(set(only_fields) & set(fields))
        return fields
