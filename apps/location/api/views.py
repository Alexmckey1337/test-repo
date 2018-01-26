# -*- coding: utf-8
from __future__ import unicode_literals

from django_filters import rest_framework
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from apps.location.models import OldCountry, OldRegion, OldCity
from apps.location.api.serializers import OldCountrySerializer, OldRegionSerializer, OldCitySerializer


class OldCountryViewSet(viewsets.ModelViewSet):
    queryset = OldCountry.objects.all()
    serializer_class = OldCountrySerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('title',)
    filter_fields = []
    permission_classes = (IsAuthenticated,)


class OldRegionViewSet(viewsets.ModelViewSet):
    queryset = OldRegion.objects.all()
    serializer_class = OldRegionSerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('title',)
    filter_fields = ['country']
    permission_classes = (IsAuthenticated,)


class OldCityViewSet(viewsets.ModelViewSet):
    queryset = OldCity.objects.all()
    serializer_class = OldCitySerializer
    pagination_class = None
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,)
    search_fields = ('title',)
    filter_fields = ['region', 'country']
    permission_classes = (IsAuthenticated,)
