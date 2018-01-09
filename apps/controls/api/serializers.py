from rest_framework import serializers
from apps.account.models import CustomUser
from apps.account.api.serializers import HierarchyTitleSerializer


class DatabaseAccessSerializer(serializers.ModelSerializer):
    hierarchy = serializers.CharField(source='hierarchy.title', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'fullname', 'hierarchy', 'is_staff', 'is_active', 'can_login')
