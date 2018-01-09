# -*- coding: utf-8
from apps.account.models import CustomUser
from apps.controls.api.serializers import DatabaseAccessSerializer
from rest_framework.decorators import list_route, detail_route
from common.views_mixins import ModelWithoutDeleteViewSet
from rest_framework.generics import get_object_or_404
from rest_framework import status, exceptions, mixins, viewsets
from django.db import transaction, IntegrityError
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _


class DatabaseAccessViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.select_related(
        'hierarchy', 'master__hierarchy').prefetch_related(
        'divisions', 'departments'
    )

    serializer_class = DatabaseAccessSerializer

    @list_route(methods=['POST'])
    def submit(self, request):
        data = request.data.get('data')  # {"data": [{"user_id": 20782, "is_staff": true, "can_login": true}]}
        if not data:
            raise exceptions.ValidationError({'message': _('Parameter {data} must is required')})

        for obj in data:
            user_id = obj.pop('user_id')
            if not user_id:
                raise exceptions.ValidationError(
                    {'message': _('Parameter {user_id} must be passed for each object in {data}')})

            user = get_object_or_404(CustomUser, pk=user_id)

            try:
                with transaction.atomic():
                    for k, v in obj.items():
                        if k not in ['is_staff', 'is_active', 'can_login']:
                            raise exceptions.ValidationError(
                                {'message': _('Field names must be one of [is_staff, is_active, can_login]')}
                            )
                        setattr(user, k, v)
                        user.save()

            except IntegrityError:
                data = {'message': _('При сохранение возникла ошибка. Попробуйте еще раз')}
                return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response({'message': _('Успешно сохранено')}, status=status.HTTP_200_OK)
