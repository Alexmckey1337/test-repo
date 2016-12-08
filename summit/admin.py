# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats import base_formats

from summit.admin_filters import HasTicketListFilter, HasEmailListFilter
from .models import SummitAnket, Summit, SummitType, SummitAnketNote, SummitLesson, AnketEmail, SummitUserConsultant
from .resources import SummitAnketResource
from .tasks import send_tickets, create_tickets


class SummitUserConsultantInline(admin.TabularInline):
    model = SummitUserConsultant
    fk_name = 'user'


class SummitTypeAdmin(admin.ModelAdmin):
    fields = ('title', 'club_name', 'image')
    list_display = ('title', 'club_name')


class SummitLessonInline(admin.TabularInline):
    fields = ('name', 'summit')
    model = SummitLesson


class SummitAdmin(admin.ModelAdmin):
    # filter_horizontal = ('consultants',)
    inlines = [SummitLessonInline, ]


class SummitAnketNoteInline(admin.TabularInline):
    model = SummitAnketNote


class AnketEmailAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'attach', 'is_success')
    search_fields = ('anket__user__last_name', 'anket__user__email', 'recipient')
    list_filter = ('anket__summit', 'is_success', 'created_at')
    date_hierarchy = 'created_at'
    change_list_filter_template = "admin/filter_listing.html"
    change_list_template = "admin/change_list_filter_sidebar.html"

    def __init__(self, model, admin_site):
        super(AnketEmailAdmin, self).__init__(model, admin_site)

        self.readonly_fields = [field.name for field in model._meta.fields]
        self.readonly_model = model


class SummitAnketAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'user', 'summit', 'code', 'visited', 'is_member', 'role')
    list_editable = ('visited',)
    readonly_fields = ('user', 'summit')
    list_filter = ('summit', 'user__department', 'protected',
                   HasTicketListFilter, HasEmailListFilter,
                   # TODO very slow
                   # PaidStatusListFilter,
                   )
    change_list_filter_template = "admin/filter_listing.html"
    search_fields = ['code', 'user__last_name', ]

    actions = ['send_tickets', 'create_tickets']

    resource_class = SummitAnketResource
    formats = (base_formats.XLSX,)

    inlines = [
        # SummitAnketNoteInline,
        SummitUserConsultantInline
    ]

    class Meta:
        model = SummitAnket

    def send_tickets(self, request, queryset):
        send_tickets.delay(list(queryset.values_list('id', flat=True)))

    send_tickets.short_description = "Отправить билеты выбранным пользователям"

    def create_tickets(self, request, queryset):
        ankets = list(queryset.values('id', 'code',
                                      'user__first_name', 'user__last_name', 'user__middle_name'))
        for a in ankets:
            a['fullname'] = '{} {} {}'.format(a['user__first_name'], a['user__last_name'], a['user__middle_name'])
        create_tickets.delay(ankets)

    create_tickets.short_description = "Сгенерировать билеты выбранным пользователям"


admin.site.register(SummitAnket, SummitAnketAdmin)
admin.site.register(Summit, SummitAdmin)
admin.site.register(SummitType, SummitTypeAdmin)
admin.site.register(AnketEmail, AnketEmailAdmin)
