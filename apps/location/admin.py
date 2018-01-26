# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from apps.location.models import OldCountry, OldRegion, OldCity


class OldCountryAdmin(admin.ModelAdmin):
    list_display = ('title', 'phone_code',)
    search_fields = ['title']

    class Meta:
        model = OldCountry


admin.site.register(OldCountry, OldCountryAdmin)


class OldRegionAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']

    class Meta:
        model = OldRegion


admin.site.register(OldRegion, OldRegionAdmin)


class OldCityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ['title']

    class Meta:
        model = OldCity


admin.site.register(OldCity, OldCityAdmin)
