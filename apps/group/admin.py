from django.contrib import admin
from apps.group.models import Church, HomeGroup, Direction


class ChurchAdmin(admin.ModelAdmin):
    search_fields = ('title',)
    autocomplete_fields = ('locality', 'pastor')
    list_display = ('title', 'pastor', 'city', 'address', 'locality')

    class Meta:
        model = Church


class HomeGroupAdmin(admin.ModelAdmin):
    search_fields = ('locality__name', 'leader__first_name', 'leader__middle_name', 'leader__last_name')
    autocomplete_fields = ('locality', 'leader', 'church')
    list_display = ('title', 'leader', 'city', 'address', 'locality', 'church')
    readonly_fields = (
        # 'leader',
        # 'church',
        # 'locality',
    )

    class Meta:
        model = HomeGroup


class DirectionAdmin(admin.ModelAdmin):
    list_display = ('title_ru', 'title_en', 'title_de', 'code')

    class Meta:
        model = Direction


admin.site.register(Church, ChurchAdmin)
admin.site.register(HomeGroup, HomeGroupAdmin)
admin.site.register(Direction, DirectionAdmin)
