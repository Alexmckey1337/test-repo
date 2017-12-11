# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from apps.navigation.models import Navigation, Table, ColumnType, Category, Column


class NavigationAdmin(admin.ModelAdmin):
    list_display = ('title', 'url',)

    class Meta:
        model = Navigation


admin.site.register(Navigation, NavigationAdmin)


class ColumnInline(admin.TabularInline):
    model = Column


class TableAdmin(admin.ModelAdmin):
    list_display = ('user',)
    inlines = (ColumnInline,)

    class Meta:
        model = Table


admin.site.register(Table, TableAdmin)


class ColumnTypeTAdmin(admin.ModelAdmin):
    list_display = ('title', 'verbose_title', 'ordering_title', 'category',)
    list_filter = ('category',)

    class Meta:
        model = ColumnType


admin.site.register(ColumnType, ColumnTypeTAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'common',)

    class Meta:
        model = Category


admin.site.register(Category, CategoryAdmin)


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('table',)

    class Meta:
        model = Column


admin.site.register(Column, ColumnAdmin)
