from django.contrib import admin
from models import UserReport, WeekReport, MonthReport, YearReport


class UserReportAdmin(admin.ModelAdmin):
    list_display = ('user', )

    class Meta:
        model = UserReport

admin.site.register(UserReport, UserReportAdmin)


class WeekReportAdmin(admin.ModelAdmin):
    list_display = ('user', )

    class Meta:
        model = WeekReport

admin.site.register(WeekReport, WeekReportAdmin)


class MonthReportAdmin(admin.ModelAdmin):
    list_display = ('user', )

    class Meta:
        model = MonthReport

admin.site.register(MonthReport, MonthReportAdmin)


class YearReportAdmin(admin.ModelAdmin):
    list_display = ('user', )

    class Meta:
        model = YearReport

admin.site.register(YearReport, YearReportAdmin)