# -*- coding: utf-8
from __future__ import unicode_literals

from collections import Counter

from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework import exceptions
from rest_framework import viewsets, filters, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.location.api.serializers import OldCountrySerializer, OldRegionSerializer, OldCitySerializer
from apps.location.models import OldCountry, OldRegion, OldCity, City, District


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


class CitySearch:
    def __init__(self):
        self.cities = []
        self.countries = []
        self.areas = []
        self.districts = []

    def add_city(self, city, country, area, district, score=1):
        self.cities.append({
            'city': city,
            'country': country,
            'area': area,
            'district': district,
            'score': score,
        })

    def add_country(self, name, count):
        self.countries.append({'name': name, 'count': count})

    def add_area(self, name, count):
        self.areas.append({'name': name, 'count': count})

    def add_district(self, name, count):
        self.districts.append({'name': name, 'count': count})

    @property
    def data(self):
        return {
            'cities': self.cities,
            'filters': {
                'countries': self.countries,
                'areas': self.areas,
                'districts': self.districts,
            }
        }


class CitySearchListView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        city = request.query_params.get('city', '')
        if len(city) < 3:
            raise exceptions.ValidationError({'search': _('Length of search query must be > 2')})
        country = request.query_params.get('country')
        area = request.query_params.get('area')
        district = request.query_params.get('district')
        force_pg = request.query_params.get('force_pg', None)

        c = Elasticsearch('es')
        if c.ping() and force_pg is None:
            ret = self.get_es_data(c, city, country, area, district)
        else:
            ret = self.get_pg_data(city, country, area, district)

        return Response(data=ret)

    def get_es_data(self, c, city, country, area, district):
        ret = CitySearch()

        s = Search(using=c, index='vocrm').query('match', name=city)
        s.aggs.bucket('countries', 'terms', field='country.name.keyword', min_doc_count=1, size=100)
        s.aggs.bucket('areas', 'terms', field='area.name.keyword', min_doc_count=1, size=100)
        s.aggs.bucket('districts', 'terms', field='district.name.keyword', min_doc_count=1, size=100)
        if country:
            s = s.query('match', country__name__keyword=country)
        if area:
            s = s.query('match', area__name__keyword=area)
        if district:
            s = s.query('match', district__name__keyword=district)
        s = s[:100]
        r = s.execute()
        for h in r:
            ret.add_city(
                h.name,
                h.country.name if hasattr(h, 'country') else '',
                h.area.name if hasattr(h, 'area') else '',
                h.district.name if hasattr(h, 'district') else '',
                h.meta.score
            )
        for t in r.aggregations.countries.buckets:
            ret.add_country(t.key, t.doc_count)
        for t in r.aggregations.areas.buckets:
            ret.add_area(t.key, t.doc_count)
        for t in r.aggregations.districts.buckets:
            ret.add_district(t.key, t.doc_count)
        return ret.data

    def get_pg_data(self, city, country, area, district):
        city = city.strip()
        ret = CitySearch()
        base_cities = City.objects.select_related('country', 'area').filter(name__istartswith=city)
        if country:
            base_cities = base_cities.filter(country__name=country)
        if area:
            base_cities = base_cities.filter(area__name=area)
        if district:
            base_cities = base_cities.filter(rajon__in=District.objects.filter(name=district))
        cities = base_cities[:100]
        dd = set(cities.values_list('rajon', flat=True)) - {None}
        districts = {d['id']: d['name']
                     for d in District.objects.filter(pk__in=dd).values('id', 'name')}
        for c in cities:
            ret.add_city(
                c.name,
                c.country.name if c.country else '',
                c.area.name if c.area else '',
                districts.get(c.rajon, '')
            )
        districts = {d['id']: d['name']
                     for d in District.objects.values('id', 'name')}
        for c, n in Counter(base_cities.values_list('country__name', flat=True)).most_common(100):
            ret.add_country(c, n)
        for a, n in Counter(base_cities.values_list('area__name', flat=True)).most_common(100):
            ret.add_area(a, n)
        for d, n in Counter(base_cities.values_list('rajon', flat=True)).most_common(100):
            ret.add_district(districts.get(d, '?'), n)
        return ret.data
