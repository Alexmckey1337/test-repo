# -*- coding: utf-8
from __future__ import unicode_literals

from django.contrib import admin

from .models import Event, Participation, EventType, EventAnket, Week


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


admin.site.register(Participation, ParticipationAdmin)
