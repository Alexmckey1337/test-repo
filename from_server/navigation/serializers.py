from models import Navigation
from rest_framework import serializers


class NavigationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Navigation
        fields = ('title', 'url', )
