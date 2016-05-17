from account.models import CustomUser as User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    #fields = serializers.OrderedDict()
    #master_leaderships = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'email', 'fullname',
                  'first_name', 'last_name', 'middle_name',
                  'is_active', 'is_staff', 'phone_number',
                  'image', 'born_date', 'facebook', 'vkontakte',
                  'hierarchy', 'hierarchy_name', 'department', 'reports', 'my_reports',
                  'participations', 'my_reports',
                  'country', 'region', 'city', 'district', 'address',
                  'description', 'skype', 'fields',
                  'master', 'disciples', 'common', 'fields', )
