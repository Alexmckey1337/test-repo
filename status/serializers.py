from models import Status, Division
from rest_framework import serializers


class StatusSerializer(serializers.HyperlinkedModelSerializer):
    #day = serializers.IntegerField(read_only=True)

    class Meta:
        model = Status
        fields = ('url', 'id', 'title',)


class DivisionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Division
        fields = ('url', 'id', 'title',)