from account.models import CustomUser as User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'fullname', 'image',
                  'hierarchy_name', 'has_disciples', 'hierarchy_order', 'column_table',
                  'fields', 'division_fields', 'hierarchy_chain', 'partnerships_info')


class UserShortSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'fullname')
