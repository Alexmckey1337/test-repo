# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from apps.event.models import (
    MeetingAttend, Meeting, MeetingType, ChurchReport, Event, Participation, EventType, EventAnket, Week)


class WeekAdmin(admin.ModelAdmin):
    list_display = ('week',)

    class Meta:
        model = EventType


admin.site.register(Week, WeekAdmin)


class EventTypeAdmin(admin.ModelAdmin):
    list_display = ('title',)

    class Meta:
        model = EventType


admin.site.register(EventType, EventTypeAdmin)


class EventAnketAdmin(admin.ModelAdmin):
    list_display = ('user',)

    class Meta:
        model = EventAnket


admin.site.register(EventAnket, EventAnketAdmin)


class EventAdmin(admin.ModelAdmin):
    list_display = ('id',)

    class Meta:
        model = Event


admin.site.register(Event, EventAdmin)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'check',)

    class Meta:
        model = Participation


# class ChurchReportPastorAdmin(admin.ModelAdmin):
#     list_display = ('id',)
#
#     class Meta:
#         model = ChurchReportPastor


admin.site.register(Participation, ParticipationAdmin)
admin.site.register(MeetingType)
admin.site.register(Meeting)
admin.site.register(MeetingAttend)
admin.site.register(ChurchReport)
