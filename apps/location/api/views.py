from collections import Counter

from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from rest_framework import exceptions
from rest_framework import viewsets, filters, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.location.api.permissions import VoCanSeeCities
from apps.location.api.serializers import OldCountrySerializer, OldRegionSerializer, OldCitySerializer
from apps.location.models import OldCountry, OldRegion, OldCity, City, District, Country, Area


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

    def add_city(self, city, location, country, area, district, pk, score=1):
        self.cities.append({
            'pk': pk,
            'city': city,
            'location': location,
            'country': country,
            'area': area,
            'district': district,
            'score': score,
        })

    def add_country(self, pk, name, count):
        self.countries.append({'pk': pk, 'name': name, 'count': count})

    def add_area(self, pk, name, count):
        self.areas.append({'pk': pk, 'name': name, 'count': count})

    def add_district(self, pk, name, count):
        self.districts.append({'pk': pk, 'name': name, 'count': count})

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
    permission_classes = (IsAuthenticated,)

    min_city_length = 3

    def get(self, request, *args, **kwargs):
        city = request.query_params.get('city', '')
        if len(city) < self.min_city_length:
            raise exceptions.ValidationError({'search': _('Length of search query must be > %s') % max(self.min_city_length - 1, 0)})
        country = request.query_params.get('country')
        area = request.query_params.get('area')
        district = request.query_params.get('district')
        country_id = request.query_params.get('country_id', '').upper()
        area_id = request.query_params.get('area_id')
        district_id = request.query_params.get('district_id')
        force_pg = request.query_params.get('force_pg', None)

        c = Elasticsearch('es')
        if c.ping() and force_pg is None:
            ret = self.get_es_data(c, city, country, area, district, country_id, area_id, district_id)
        else:
            ret = self.get_pg_data(city, country, area, district, country_id, area_id, district_id)

        return Response(data=ret)

    def get_es_data(self, c, city, country, area, district, country_id, area_id, district_id):
        ret = CitySearch()

        s = Search(using=c, index='city').query('match', city={'query': city, 'operator': 'and'})
        s.aggs.bucket('countries', 'terms', field='country.id', min_doc_count=1, size=100)
        s.aggs.bucket('areas', 'terms', field='area.id', min_doc_count=1, size=100)
        s.aggs.bucket('districts', 'terms', field='district.id', min_doc_count=1, size=100)
        if country:
            s = s.query('match', country__name__keyword=country)
        if area:
            s = s.query('match', area__name__keyword=area)
        if district:
            s = s.query('match', district__name__keyword=district)
        if country_id:
            s = s.query('match', country__id=country_id)
        if area_id:
            s = s.query('match', area__id=area_id)
        if district_id:
            s = s.query('match', district__id=district_id)
        s = s[:100]
        r = s.execute()
        for h in r:
            ret.add_city(
                h.name,
                h.location.to_dict() if hasattr(h, 'location') else {},
                h.country.name if hasattr(h, 'country') else '',
                h.area.name if hasattr(h, 'area') else '',
                h.district.name if hasattr(h, 'district') else '',
                h.pk,
                h.meta.score
            )
        country_keys = list()
        for t in r.aggregations.countries.buckets:
            country_keys.append(t.key)
        country_objects = Country.objects.in_bulk(country_keys)
        area_keys = list()
        for t in r.aggregations.areas.buckets:
            area_keys.append(t.key)
        area_objects = Area.objects.in_bulk(area_keys)
        district_keys = list()
        for t in r.aggregations.districts.buckets:
            district_keys.append(t.key)
        district_objects = District.objects.in_bulk(district_keys)
        for t in r.aggregations.countries.buckets:
            ret.add_country(t.key, getattr(country_objects.get(t.key, '???'), 'name', '???'), t.doc_count)
        for t in r.aggregations.areas.buckets:
            ret.add_area(t.key, getattr(area_objects.get(t.key, '???'), 'name', '???'), t.doc_count)
        for t in r.aggregations.districts.buckets:
            ret.add_district(t.key, getattr(district_objects.get(t.key, '???'), 'name', '???'), t.doc_count)
        return ret.data

    def get_pg_data(self, city, country, area, district, country_id, area_id, district_id):
        city = city.strip()
        ret = CitySearch()
        base_cities = City.objects.select_related('country', 'area').filter(name__istartswith=city)
        if country:
            base_cities = base_cities.filter(country__name=country)
        if area:
            base_cities = base_cities.filter(area__name=area)
        if district:
            base_cities = base_cities.filter(rajon__in=District.objects.filter(name=district))
        if country_id:
            base_cities = base_cities.filter(country_id=country_id)
        if area_id:
            base_cities = base_cities.filter(area_id=area_id)
        if district_id:
            base_cities = base_cities.filter(rajon=district_id)
        cities = base_cities[:100]
        dd = set(cities.values_list('rajon', flat=True)) - {None}
        districts = {d['id']: d['name']
                     for d in District.objects.filter(pk__in=dd).values('id', 'name')}
        for c in cities:
            ret.add_city(
                c.name,
                {'lat': c.latitude, 'lon': c.longitude},
                c.country.name if c.country else '',
                c.area.name if c.area else '',
                districts.get(c.rajon, ''),
                c.id,
            )
        districts = {d['id']: d['name']
                     for d in District.objects.values('id', 'name')}
        for c, n in Counter(base_cities.values_list('country__name', 'country_id')).most_common(100):
            ret.add_country(c[1], c[0], n)
        for a, n in Counter(base_cities.values_list('area__name', 'area_id')).most_common(100):
            ret.add_area(a[1], a[0], n)
        for d, n in Counter(base_cities.values_list('rajon', flat=True)).most_common(100):
            ret.add_district(d, districts.get(d, '???'), n)
        return ret.data


class VoCitySearchListView(CitySearchListView):
    permission_classes = (VoCanSeeCities,)
    min_city_length = 2
