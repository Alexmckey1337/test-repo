# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin
from import_export.admin import ExportMixin
from import_export.formats import base_formats

from summit.admin_filters import HasTicketListFilter
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
    list_display = ('__str__', 'attach')
    readonly_fields = ('anket',)
    list_filter = ('anket__summit',)


class SummitAnketAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'user', 'summit', 'code', 'visited', 'is_member', 'role')
    list_editable = ('visited',)
    readonly_fields = ('user', 'summit')
    list_filter = ('summit', 'user__department', 'protected', HasTicketListFilter)
    search_fields = ['code', 'user__last_name', ]

    # actions = ['send_tickets', 'create_tickets']

    resource_class = SummitAnketResource
    formats = (base_formats.XLSX,)

    inlines = [
        # SummitAnketNoteInline,
        SummitUserConsultantInline
    ]

    class Meta:
        model = SummitAnket

    def send_tickets(self, request, queryset):
        ankets = list(queryset.values('id', 'user__email', 'summit__type__title', 'summit__start_date',
                                      'user__first_name', 'user__last_name', 'user__middle_name', 'code',
                                      'ticket'))
        for a in ankets:
            d = a['summit__start_date']
            a['summit__start_date'] = '{}.{}.{}'.format(d.day, d.month, d.year)
        send_tickets.delay(ankets)

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
