from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from apps.tab_column.models import Table, Column


class ColumnInline(admin.TabularInline):
    model = Column

def сopy_table_action(modeladmin, request, queryset):
    for table in queryset:
        table_id = table.id
        table.id = None
        table.title = table.title + '_copy'
        table.save()
        for column in Column.objects.filter(table__id=table_id):
            column.id = None
            column.table = table
            column.save()


сopy_table_action.short_description = _('Копировать таблицу')


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    inlines = [ColumnInline, ]
    actions = [сopy_table_action, ]


