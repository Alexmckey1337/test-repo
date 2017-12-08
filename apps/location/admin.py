# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from apps.location.models import Country, Region, City


class CountryAdmin(admin.ModelAdmin):
    list_display = ('title', 'phone_code',)
    search_fields = ['title']

    class Meta:
        model = Country


admin.site.register(Country, CountryAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']

    class Meta:
        model = Region


admin.site.register(Region, RegionAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']

    class Meta:
        model = City


admin.site.register(City, CityAdmin)
