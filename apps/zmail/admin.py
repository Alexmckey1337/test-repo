from django.contrib import admin

from apps.zmail.models import ZMailAttachment, ZMailTemplate, ZMailAuth


class MailTemplateFileAdmin(admin.TabularInline):
    model = ZMailAttachment
    extra = 1


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'from_email', 'slug', 'is_active', 'created_at', 'updated_at')
    list_filter = (
        'is_active', 'created_at', 'updated_at',)
    search_fields = ('name', 'subject', 'slug', 'message')
    ordering = ('-id',)
    list_editable = ('is_active',)
    list_display_links = ('name',)
    date_hierarchy = 'created_at'
    inlines = [MailTemplateFileAdmin]
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(ZMailTemplate, MailTemplateAdmin)
admin.site.register(ZMailAuth)
