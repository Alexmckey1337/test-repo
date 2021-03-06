from apps.help.models import Manual
from rest_framework import viewsets, mixins
from .serializers import ManualSerializer


class ManualViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Manual.objects.all()
    serializer_class = ManualSerializer
