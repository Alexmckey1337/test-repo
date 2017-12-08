# -*- coding: utf-8
from __future__ import unicode_literals

import ast
import time
import urllib2

from location.models import Country, Region, City


def get_countries():
    link = 'https://api.vk.com/method/database.getCountries?need_all=1&count=300&lang=ru'
    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    for item in verbose_response['response']:
        _, created = Country.objects.get_or_create(code=item['cid'], defaults={'title': item['title']})
        if created:
            i += 1
    print("Got %i countries" % i)


def get_regions(countryCode):
    country = Country.objects.get(code=countryCode)
    link = 'https://api.vk.com/method/database.getRegions?country_id=%i&count=300&lang=ru' % countryCode
    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    for item in verbose_response['response']:
        _, created = Region.objects.get_or_create(code=item['region_id'],
                                                  defaults={'title': item['title'], 'country': country})
        if created:
            i += 1
    print("Got %i regions in %s" % (i, country.title))


def get_cities_by_region(regionCode, offset=0):
    region = Region.objects.get(code=regionCode)
    if not offset == 0:
        link = 'https://api.vk.com/method/database.getCities?' \
               'country_id=%i&region_id=%i&count=1000&offset=%i&need_all=1lang=ru' % (
                   region.country.code, region.code, offset)
    else:
        link = 'https://api.vk.com/method/database.getCities?' \
               'country_id=%i&region_id=%i&count=1000&need_all=1&lang=ru' % (
                   region.country.code, region.code)

    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    print(len(verbose_response['response']))
    for item in verbose_response['response']:
        _, created = City.objects.get_or_create(code=item['cid'], defaults={'title': item['title'], 'region': region})
        if created:
            i += 1
    print("Got %i cities in %s region, %s" % (i, region.title, region.country.title))
    if len(verbose_response['response']) == 1000:
        offset += 1000
        get_cities_by_region(regionCode, offset=offset)


def get_cities_by_country(country_id, offset=0):
    country = Country.objects.get(id=country_id)
    if not offset == 0:
        link = 'https://api.vk.com/method/database.getCities?country_id=%i&count=1000&offset=%i&need_all=1lang=ru' % (
            country.code, offset)
    else:
        link = 'https://api.vk.com/method/database.getCities?country_id=%i&count=1000&need_all=1&lang=ru' % (
            country.code)

    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    print(len(verbose_response['response']))
    for item in verbose_response['response']:
        _, created = City.objects.get_or_create(code=item['cid'], defaults={'title': item['title'], 'country': country})
        if created:
            i += 1
    print("Got %i cities in  %s" % (i, country.title))
    if len(verbose_response['response']) == 1000:
        offset += 1000
        get_cities_by_country(country_id, offset=offset)


def get_all_regions():
    get_countries()
    countries = Country.objects.all()
    for country in countries:
        get_regions(country.code)
        time.sleep(0.35)
    print("I'm done")


def get_all_cities(country_id):
    regions = Region.objects.filter(country__id=country_id).all()
    for region in regions.all():
        get_cities_by_region(region.code)
        time.sleep(0.25)
    get_cities_by_country(country_id)
    print("I'm done")
