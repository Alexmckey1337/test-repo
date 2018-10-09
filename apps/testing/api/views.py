from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.account.api.permissions import IsSuperUser
from apps.testing.api.serializers import TestResultSerializer
from apps.testing.models import TestResult


class TestResultViewSet(viewsets.ModelViewSet):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer
    http_method_names = ['get', 'post']
    permission_classes = (IsAuthenticated, )
