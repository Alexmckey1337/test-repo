from django.contrib import admin
from models import Navigation


class NavigationAdmin(admin.ModelAdmin):
    list_display = ('title',  'url', )
    #inlines = [ChoiceInline]

    class Meta:
        model = Navigation

admin.site.register(Navigation, NavigationAdmin)