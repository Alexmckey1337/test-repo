from django.contrib import admin

from apps.testing.models import TestResult


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_id', 'test_title', 'user', 'total_points')
    readonly_fields = ('test_id', 'test_title', 'user', 'total_points')