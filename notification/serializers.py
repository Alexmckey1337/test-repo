from models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    theme = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = ('url', 'id', 'theme', 'fullname', 'uid', 'description', 'date', 'common', 'system', )
