# -*- coding: utf-8
from apps.account.models import CustomUser
from rest_framework.decorators import list_route, detail_route
from common.views_mixins import ModelWithoutDeleteViewSet
from rest_framework.generics import get_object_or_404
from rest_framework import status, exceptions, mixins, viewsets
from django.db import transaction, IntegrityError
from rest_framework.response import Response
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import status, filters, exceptions
from common.filters import FieldSearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser
from apps.summit.models import Summit, SummitType
from apps.controls.api.serializers import (
    DatabaseAccessListSerializer, DatabaseAccessDetailSerializer, SummitPanelListSerializer,
    SummitPanelDetailSerializer, SummitPanelCreateUpdateSerializer, SummitTypePanelSerializer
)
from .filters import SummitPanelDateFilter


class DatabaseAccessViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.select_related(
        'hierarchy', 'master__hierarchy').prefetch_related(
        'divisions', 'departments'
    ).order_by('last_name', 'first_name', 'middle_name')

    serializer_list_class = DatabaseAccessListSerializer
    serializer_retrieve_class = DatabaseAccessDetailSerializer

    permission_classes = (IsAdminUser,)

    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       )

    filter_fields = ('is_staff', 'is_active', 'can_login', 'hierarchy')

    ordering_fields = ('is_staff', 'is_active', 'can_login', 'hierarchy__level', 'last_name')

    field_search_fields = {
        'search_fio': ('first_name', 'last_name', 'middle_name')
    }

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update']:
            return self.serializer_retrieve_class
        return self.serializer_list_class

    @list_route(methods=['POST'])
    def submit(self, request):
        data = request.data.get('data')  # {"data": [{"user_id": 20782, "is_staff": true, "can_login": true}]}
        if not data:
            raise exceptions.ValidationError({'message': _('Parameter {data} is required')})

        for obj in data:
            user_id = obj.pop('user_id', None)
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


class SummitPanelViewSet(ModelWithoutDeleteViewSet):
    queryset = Summit.objects.order_by('-end_date')

    serializer_list_class = SummitPanelListSerializer
    serializer_retrieve_class = SummitPanelDetailSerializer
    serializer_create_update_class = SummitPanelCreateUpdateSerializer

    permission_classes = (IsAdminUser,)

    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       )

    ordering_fields = ('type', 'status', 'start_date', 'end_date')

    filter_class = SummitPanelDateFilter

    field_search_fields = {
        'search_title': ('type__title',)
    }

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action == 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_create_update_class


class SummitTypePanelViewSet(ModelWithoutDeleteViewSet):
    queryset = SummitType.objects.all()
    serializer_class = SummitTypePanelSerializer
    permission_classes = (IsAdminUser,)
