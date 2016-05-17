from django.contrib import admin
from models import Event, Participation


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'day', 'active', 'cyclic', )

    class Meta:
        model = Event

admin.site.register(Event, EventAdmin)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'check', )

    class Meta:
        model = Participation

admin.site.register(Participation, ParticipationAdmin)