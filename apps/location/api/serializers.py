# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from apps.location.models import Country, Region, City


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'title', 'code', 'phone_code',)


class RegionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'title',)


class CitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'title',)
