import urllib2
import ast
from models import Country, Region, City
import time


def getCountries():
    link = 'https://api.vk.com/method/database.getCountries?need_all=1&count=300&lang=ru'
    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    for item in verbose_response['response']:
        try:
            country = Country.objects.get(code=item['cid'])
            pass
        except Country.DoesNotExist:
            country = Country.objects.create(title=item['title'],
                                             code=item['cid'])
            i += 1
    print "Got %i countries" % i



def getRegions(countryCode):
    country = Country.objects.get(code=countryCode)
    link = 'https://api.vk.com/method/database.getRegions?country_id=%i&count=300&lang=ru' % countryCode
    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    for item in verbose_response['response']:
        try:
            region = Region.objects.get(code=item['region_id'])
            pass
        except Region.DoesNotExist:
            region = Region.objects.create(title=item['title'],
                                           code=item['region_id'],
                                           country=country)
            i += 1
    print "Got %i regions in %s" % (i, country.title)


def getCitiesByRegion(regionCode, offset=0):
    region = Region.objects.get(code=regionCode)
    if not offset == 0:
        link = 'https://api.vk.com/method/database.getCities?country_id=%i&region_id=%i&count=1000&offset=%i&need_all=1lang=ru' % (region.country.code, region.code, offset)
    else:
        link = 'https://api.vk.com/method/database.getCities?country_id=%i&region_id=%i&count=1000&need_all=1&lang=ru' % (region.country.code, region.code)


    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    print len(verbose_response['response'])
    for item in verbose_response['response']:
        try:
            city = City.objects.get(code=item['cid'])
            i += 1
        except City.DoesNotExist:
            city = City.objects.create(title=item['title'],
                                       code=item['cid'],
                                       region=region)
            i += 1
    print "Got %i cities in %s region, %s" % (i, region.title, region.country.title)
    if len(verbose_response['response']) == 1000:
        offset += 1000
        getCitiesByRegion(regionCode, offset=offset)


def getCitiesByCountry(country_id, offset=0):
    country = Country.objects.get(id=country_id)
    if not offset == 0:
        link = 'https://api.vk.com/method/database.getCities?country_id=%i&count=1000&offset=%i&need_all=1lang=ru' % (country.code, offset)
    else:
        link = 'https://api.vk.com/method/database.getCities?country_id=%i&count=1000&need_all=1&lang=ru' % (country.code)


    filehandle = urllib2.urlopen(link)
    response = filehandle.read()
    verbose_response = ast.literal_eval(response)
    i = 0
    print len(verbose_response['response'])
    for item in verbose_response['response']:
        try:
            city = City.objects.get(code=item['cid'])
            i += 1
        except City.DoesNotExist:
            city = City.objects.create(title=item['title'],
                                       code=item['cid'],
                                       country=country)
            i += 1
    print "Got %i cities in  %s" % (i, country.title)
    if len(verbose_response['response']) == 1000:
        offset += 1000
        getCitiesByCountry(country_id, offset=offset)

def getAllRegions():
    getCountries()
    countries = Country.objects.all()
    for country in countries:
        getRegions(country.code)
        time.sleep(0.35)
    print "I'm done"

def getAllCities(country_id):
    regions = Region.objects.filter(country__id=country_id).all()
    for region in regions.all():
        getCitiesByRegion(region.code)
        time.sleep(0.25)
    getCitiesByCountry(country_id)
    print "I'm done"

