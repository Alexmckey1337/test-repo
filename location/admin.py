from django.contrib import admin
from models import Country, Region, City


class CountryAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = Country

admin.site.register(Country, CountryAdmin)


class RegionAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = Region

admin.site.register(Region, RegionAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ('title', )

    class Meta:
        model = City

admin.site.register(City, CityAdmin)
