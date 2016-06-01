from models import Country, Region, City
from rest_framework import serializers


class CountrySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'title', 'code', )


class RegionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Region
        fields = ('id', 'title', )


class CitySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = City
        fields = ('id', 'title', )
