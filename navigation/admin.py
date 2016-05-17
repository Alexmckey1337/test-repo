from django.contrib import admin
from models import Navigation, Table, ColumnType, Category, Column


class NavigationAdmin(admin.ModelAdmin):
    list_display = ('title',  'url', )

    class Meta:
        model = Navigation

admin.site.register(Navigation, NavigationAdmin)


class TableAdmin(admin.ModelAdmin):
    list_display = ('user', )

    class Meta:
        model = Table

admin.site.register(Table, TableAdmin)


class ColumnTypeTAdmin(admin.ModelAdmin):
    list_display = ('title', 'verbose_title', 'ordering_title', )

    class Meta:
        model = ColumnType

admin.site.register(ColumnType, ColumnTypeTAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'common', )

    class Meta:
        model = Category

admin.site.register(Category, CategoryAdmin)


class ColumnAdmin(admin.ModelAdmin):
    list_display = ('table', )

    class Meta:
        model = Column

admin.site.register(Column, ColumnAdmin)
