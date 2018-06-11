from django.contrib import admin
from apps.group.models import Church, HomeGroup, Direction


class ChurchAdmin(admin.ModelAdmin):
    search_fields = ('locality', 'pastor')
    list_display = ('title', 'pastor', 'city', 'address', 'locality')

    class Meta:
        model = Church


class HomeGroupAdmin(admin.ModelAdmin):
    search_fields = ('locality', 'leader')
    list_display = ('title', 'leader', 'city', 'address', 'locality')

    class Meta:
        model = HomeGroup


class DirectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'code')

    class Meta:
        model = Direction


admin.site.register(Church, ChurchAdmin)
admin.site.register(HomeGroup, HomeGroupAdmin)
admin.site.register(Direction, DirectionAdmin)
