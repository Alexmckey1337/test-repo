from models import Status
from rest_framework import serializers


class StatusSerializer(serializers.HyperlinkedModelSerializer):
    #day = serializers.IntegerField(read_only=True)

    class Meta:
        model = Status
        fields = ('url', 'id', 'title',)
