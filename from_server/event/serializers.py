from models import Event, Participation
from rest_framework import serializers


class EventSerializer(serializers.HyperlinkedModelSerializer):
    day = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = ('url', 'id', 'title', 'date', 'day', 'active', 'cyclic', )


class ParticipationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Participation
        fields = ('url', 'id', 'user',  'event', 'check', 'description', 'common', 'fields', )
