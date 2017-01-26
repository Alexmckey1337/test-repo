# -*- coding: utf-8
import django_filters
from common.filters import FieldSearchFilter

from django.db.models import Count, Q
from rest_framework import status
from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hierarchy.models import Department
from account.models import CustomUser
from .models import HomeGroup, Church
from .serializers import ChurchSerializer, ChurchDetailSerializer, ChurchListSerializer
from .serializers import HomeGroupSerializer, HomeGroupDetailSerializer, HomeGroupListSerializer
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


class ChurchAllUsersListView(mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = CustomUser.objects.exclude(Q(home_groups__isnull=True), Q(churches__isnull=True))
    serializer_class = HomeGroupUserSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter)

    ordering_fields = ('fullname', 'phone_number', 'repentance_date', 'spiritual_level',
                       'born_date',)

    search_fields = ('fullname', 'phone_number', 'repentance_date', 'spiritual_level',
                     'born_date',)

    filter_fields = ('first_name', 'last_name', 'phone_number', 'spiritual_level',)

    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination


class ChurchFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(name='department', queryset=Department.objects.all())
    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        hierarchy__level__gt=1))

    class Meta:
        model = Church
        fields = ['department', 'pastor']


class ChurchViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = Church.objects.all()

    serializer_class = ChurchSerializer
    serializer_list_class = ChurchListSerializer
    serializer_retrieve_class = ChurchDetailSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)

    ordering_fields = ('title', 'city', 'department', 'home_group',
                       'is_open', 'opening_date', 'pastor', 'phone_number', 'address',
                       'users', 'website', 'display_title')

    search_fields = ('title', 'city', 'department', 'home_group',
                     'is_open', 'opening_date', 'pastor', 'phone_number', 'address',
                     'users', 'website', 'display_title')

    field_search_fields = {
        'search_title': ('title',),
        'search_country': ('country',),
        'search_city': ('city',),
        'search_is_open': ('is_open',),
        'search_phone_number': ('phone_number',)
    }
    filter_class = ChurchFilter

    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination

    def get_serializer_class(self):
        if self.action in 'list':
            return self.serializer_list_class
        if self.action in 'retrieve':
            return self.serializer_retrieve_class
        return self.serializer_class

    def get_queryset(self):
        if self.action in 'list':
            return self.queryset.annotate(
                count_groups=Count('home_group', distinct=True),
                count_users=Count('users', distinct=True) + Count('home_group__users', distinct=True))
        return self.queryset

    @detail_route(methods=['get'])
    def users(self, request, pk):
        serializer = HomeGroupUserSerializer
        church = get_object_or_404(Church, pk=pk)
        queryset = church.users
        serializer = serializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        if page is not None:
            serializers = HomeGroupUserSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializers.data)
        serializers = HomeGroupUserSerializer(serializer.data, many=True, context={'request': request})
        return Response(serializers.data)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data['user_id']
        church = get_object_or_404(Church, pk=pk)

        if not user_id:
            return Response({"message": "Некоректные данные"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(id=user_id)
        if not user.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = user.get()
        if user.churches.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Церкви.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.home_groups.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        church.users.add(user_id)
        return Response({'message': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data['user_id']
        church = get_object_or_404(Church, pk=pk)

        if not user_id:
            return Response({"message": "Некоректные данные"},
                            status=status.HTTP_400_BAD_REQUEST)

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
                        status=status.HTTP_204_NO_CONTENT)


class HomeGroupFilter(django_filters.FilterSet):
    church = django_filters.ModelChoiceFilter(name='church', queryset=Church.objects.all())
    leader = django_filters.ModelChoiceFilter(name='leader', queryset=CustomUser.objects.filter(
        hierarchy__level__gt=0))

    class Meta:
        model = HomeGroup
        fields = ['church', 'leader']


class HomeGroupViewSet(mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    queryset = HomeGroup.objects.all()

    serializer_class = HomeGroupSerializer
    serializer_list_class = HomeGroupListSerializer
    serializer_retrieve_class = HomeGroupDetailSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)

    search_fields = ('title', 'get_title', 'church', 'city', 'leader', 'opening_date',
                     'phone_number',)

    ordering_fields = ('title', 'get_title', 'church', 'city', 'leader', 'opening_date',
                       'phone_number',)

    field_search_fields = {
        'search_title': ('title',),
        'search_city': ('city',),
        'search_is_open': ('is_open',),
        'search_phone_number': ('phone_number',),
    }
    filter_class = HomeGroupFilter

    permission_classes = (IsAuthenticated,)
    pagination_class = GroupPagination

    def get_serializer_class(self):
        if self.action in 'retrieve':
            return self.serializer_retrieve_class
        if self.action in 'list':
            return self.serializer_list_class
        return self.serializer_class

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data['user_id']
        home_group = get_object_or_404(HomeGroup, pk=pk)
        church = home_group.church

        if not user_id:
            return Response({"message": "Некоректные данные"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(id=user_id)
        if not user.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.get().home_groups.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if user.get().churches.exists() and user.get().churches.get().id != church.id:
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь является членом другой Церкви'},
                            status=status.HTTP_400_BAD_REQUEST)

        if church.users.filter(id=user_id).exists():
            church.users.remove(user_id)
            home_group.users.add(user_id)

        return Response({'message': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data['user_id']
        home_group = get_object_or_404(HomeGroup, pk=pk)
        church = home_group.church

        if not user_id:
            return Response({"message": "Некоректные данные"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not CustomUser.objects.filter(id=user_id).exists():
            return Response({'message': 'Невозможно удалить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if not home_group.users.filter(id=user_id).exists():
            return Response({'message': 'Невозможно удалить пользователя. '
                                        'Пользователь не принадлежит к данной Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        home_group.users.remove(user_id)
        church.users.add(user_id)
        return Response({'message': 'Пользователь успешно удален.'},
                        status=status.HTTP_204_NO_CONTENT)
