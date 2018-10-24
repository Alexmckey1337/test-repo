from rest_framework import serializers

from apps.manager.models import GroupsManager
from apps.group.api.serializers import UserNameWithLinkSerializer, HomeGroupSerializer, HomeGroupNameSerializer
from apps.account.api.serializers import UserSingleSerializer


class GroupManagerListSerializer(serializers.ModelSerializer):
    person = UserNameWithLinkSerializer(read_only=True, required=False)
    group = HomeGroupNameSerializer(read_only=True, required=False)

    class Meta:
        model = GroupsManager
        fields = ('id', 'person', 'group')


class GroupManagerDetailSerializer(serializers.ModelSerializer):
    person = UserSingleSerializer(read_only=True, required=False)
    group = HomeGroupSerializer(read_only=True, required=False)

    class Meta:
        model = GroupsManager
        fields = ('id', 'person', 'group')


class GroupManagerWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupsManager
        fields = ('id', 'person', 'group')


