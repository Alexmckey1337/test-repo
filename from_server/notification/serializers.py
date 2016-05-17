from models import Notification
from rest_framework import serializers


class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notification
        fields = ('url', 'id', 'theme', 'user', 'description', 'date', 'day', 'common', )
