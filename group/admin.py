# -*- coding: utf-8
from django.contrib import admin

from .models import Church, HomeGroup


class ChurchAdmin(admin.ModelAdmin):
    list_display = ('title', 'pastor', 'city', 'address')

    class Meta:
        model = Church

admin.site.register(Church, ChurchAdmin)


class HomeGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'leader', 'city', 'address')

    class Meta:
        model = HomeGroup

admin.site.register(HomeGroup, HomeGroupAdmin)
