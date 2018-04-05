from django.contrib import admin
from apps.help.models import Manual, ManualCategory


@admin.register(ManualCategory)
class ManualCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'position')

    class Meta:
        model = ManualCategory


@admin.register(Manual)
class ManualAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'position')
    list_filter = ('category',)

    class Meta:
        model = Manual


admin.register(ManualCategoryAdmin)
admin.register(ManualAdmin)
