from django.contrib import admin
from models import UserReport, DayReport, MonthReport, YearReport


class UserReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', )
    fields = ('user', 'date',)

    class Meta:
        model = UserReport

admin.site.register(UserReport, UserReportAdmin)


class YearReportAdmin(admin.ModelAdmin):
    list_display = ('date', )
    #fields = ('date',)

    class Meta:
        model = YearReport

admin.site.register(YearReport, YearReportAdmin)

class DayReportAdmin(admin.ModelAdmin):
    list_display = ('date', )
    #fields = ('date',)

    class Meta:
        model = DayReport

admin.site.register(DayReport, DayReportAdmin)

class MonthReportAdmin(admin.ModelAdmin):
    list_display = ('date', )
    #fields = ('date',)

    class Meta:
        model =MonthReport

admin.site.register(MonthReport, MonthReportAdmin)
