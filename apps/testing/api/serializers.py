from rest_framework import serializers

from apps.testing.models import TestResult


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = ('test_id', 'test_title', 'user', 'total_points')
