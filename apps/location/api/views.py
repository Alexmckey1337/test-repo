# -*- coding: utf-8
from __future__ import unicode_literals

from django_filters import rest_framework
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps.location.models import Country, Region, City
from apps.location.api.serializers import CountrySerializer, RegionSerializer, CitySerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('title',)
    filter_fields = []
    permission_classes = (IsAuthenticated,)


class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('title',)
    filter_fields = ['country']
    permission_classes = (IsAuthenticated,)


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('title',)
    filter_fields = ['region', 'country']
    permission_classes = (IsAuthenticated,)
