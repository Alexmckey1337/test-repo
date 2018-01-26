# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from apps.location.models import OldCountry, OldRegion, OldCity


class OldCountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OldCountry
        fields = ('id', 'title', 'code', 'phone_code',)


class OldRegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OldRegion
        fields = ('id', 'title',)


class OldCitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OldCity
        fields = ('id', 'title',)
