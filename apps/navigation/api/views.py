# -*- coding: utf-8
from __future__ import unicode_literals

from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.navigation.api.serializers import RedisTableSerializer


@api_view(['POST'])
def redis_update_columns(request):
    """
    POST: (id, number, active)
    """
    serializer = RedisTableSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.save(user_id=request.user.id)
    return Response(data)
