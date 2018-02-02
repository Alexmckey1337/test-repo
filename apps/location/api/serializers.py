# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework import serializers

from apps.location.models import OldCountry, OldRegion, OldCity, City


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


class CityTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')
        read_only_fields = ('name',)


class CityReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name', 'country_name', 'area_name', 'district_name')
        read_only_fields = ('name', 'country_name', 'area_name', 'district_name')