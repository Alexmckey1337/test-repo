# -*- coding: utf-8
from rest_framework import status
from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from django.db.models.functions import Concat
from django.db.models import Count, Value as V
from rest_framework.settings import api_settings

from .models import HomeGroup, Church
from account.models import CustomUser

from .serializers import ChurchSerializer, ChurchDetailSerializer, ChurchListSerializer
from .serializers import HomeGroupDetailSerializer, HomeGroupSerializer
from .serializers import HomeGroupUserSerializer


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

    def get_serializer_class(self):
        if self.action in 'list':
            return self.serializer_list_class
        if self.action in 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_class

    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)

    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination

    ordering_fields = ('address', 'city', 'department', 'department_id', 'home_group',
                       'is_open', 'opening_date', 'pastor', 'phone_number', 'title',
                       'users', 'website', 'display_title')

    def list(self, request, *args, **kwargs):
        queryset = Church.objects.annotate(
            count_groups=Count('home_group', distinct=True),
            count_users=Count('users', distinct=True) + Count('home_group__users', distinct=True),
            display_title=Concat('city', V(' '), 'pastor__last_name'),
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
        serializer.save()

    @detail_route(methods=['get'])
    def users(self, request, pk):
        serializer = HomeGroupUserSerializer
        church = get_object_or_404(Church, pk=pk)
        queryset = church.users
        serializer = serializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data['user_id']
        church = get_object_or_404(Church, pk=pk)

        if not user_id:
            return Response({"message": "Некоректные данные", 'status': False})

        if not CustomUser.objects.filter(id=user_id).exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.get(id=user_id).churches.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Церкви.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.get(id=user_id).home_groups.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        church.users.add(user_id)
        return Response({'message': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def remove_user(self, request, pk):
        user_id = request.data['user_id']
        church = get_object_or_404(Church, pk=pk)

        if not user_id:
            return Response({"message": "Некоректные данные", 'status': False})

        if not CustomUser.objects.filter(id=user_id).exists():
            return Response({'message': 'Невозможно удалить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not church.users.filter(id=user_id).exists():
            return Response({'message': 'Невозможно удалить пользователя. '
                                        'Пользователь не принадлежит к данной Церкви.'},
                            status=status.HTTP_400_BAD_REQUEST)

        church.users.remove(user_id)
        return Response({'message': 'Пользователь успешно удален из Церкви'},
                        status=status.HTTP_200_OK)


class HomeGroupViewSet(mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):

    queryset = HomeGroup.objects.annotate(
        display_title=Concat('city', V(' '), 'leader__last_name'))

    serializer_class = HomeGroupSerializer
    serializer_retrieve_class = HomeGroupDetailSerializer

    def get_serializer_class(self):
        if self.action in 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_class

    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination

    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)

    ordering_fields = ('address', 'church', 'city', 'leader', 'opening_date',
                       'phone_number', 'title', 'users', 'website', 'home_group_title')

    def create(self, request, *args, **kwargs):
        leader_id = request.data['leader']
        if CustomUser.objects.get(id=leader_id).home_group.exists():
            return Response({'message': 'Невозможно создать группу. '
                                        'Указанный лидер уже является членом Домашней Группы.'},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def perform_create(serializer):
        home_group = serializer.save()
        leader = home_group.leader
        church = home_group.church
        if church.users.filter(id=leader.id).exists():
            church.users.remove(leader)
        home_group.users.add(leader)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data['user_id']
        home_group = get_object_or_404(HomeGroup, pk=pk)
        church = home_group.church

        if not user_id:
            return Response({"message": "Некоректные данные", 'status': False})

        if not CustomUser.objects.filter(id=user_id).exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.get(id=user_id).home_groups.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if church.users.filter(id=user_id).exists():
            church.users.remove(user_id)

        home_group.users.add(user_id)
        return Response({'message': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def remove_user(self, request, pk):
        user_id = request.data['user_id']
        home_group = get_object_or_404(HomeGroup, pk=pk)
        church = home_group.church

        if not user_id:
            return Response({"message": "Некоректные данные", 'status': False})

        if not CustomUser.objects.filter(id=user_id).exists():
            return Response({'message': 'Невозможно удалить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not home_group.users.filter(id=user_id).exists():
            return Response({'message': 'Невозможно удалить пользователя. '
                                        'Пользователь не принадлежит к данной Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        church.users.add(user_id)
        home_group.users.remove(user_id)
        return Response({'message': 'Пользователь успешно удален.'},
                        status=status.HTTP_204_NO_CONTENT)
