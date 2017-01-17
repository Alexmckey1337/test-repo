# -*- coding: utf-8
from rest_framework import status
from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404

from django.db.models import CharField, Count, Case, When
from django.db.models import Value as V
from rest_framework.settings import api_settings

from .models import HomeGroup, Church
from .serializers import ChurchSerializer, ChurchDetailSerializer, ChurchListSerializer
from .serializers import HomeGroupDetailSerializer, HomeGroupSerializer
from .serializers import GroupUserSerializer


class GroupPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data,
        })


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class ChurchViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Church.objects.all()

    serializer_class = ChurchSerializer
    serializer_list_class = ChurchListSerializer
    serializer_retrieve_class = ChurchDetailSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination

    def list(self, request, *args, **kwargs):
        queryset = Church.objects.annotate(
            count_groups=Count('home_group', distinct=True),
            count_users=Count('users', distinct=True),
            display_title=Case(
                When(title='', then=V('get_title')),
                default='title',
                output_field=CharField())
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def perform_create(serializer):
        ch = serializer.save()
        ch.users.add(ch.pastor)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user = request.data['user_id']
        church = get_object_or_404(Church, pk=pk)
        church.users.add(user)
        data = {'message': 'Пользователь успешно добавлен.'}
        return Response(data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['get'])
    def users(self, request, pk):
        serializer = GroupUserSerializer
        church = get_object_or_404(Church, pk=pk)
        queryset = church.users
        serializer = serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in 'list':
            return self.serializer_list_class
        if self.action in 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_class


class HomeGroupViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    queryset = HomeGroup.objects.all()

    serializer_class = HomeGroupSerializer
    serializer_retrieve_class = HomeGroupDetailSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def perform_create(serializer):
        hg = serializer.save()
        hg.users.add(hg.leader)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user = request.data['user_id']
        home_group = get_object_or_404(HomeGroup, pk=pk)
        home_group.users.add(user)
        data = {'message': 'Пользователь успешно добавлен.'}
        return Response(data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.action in 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_class
