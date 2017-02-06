# -*- coding: utf-8
import django_filters
from django.db.models import Count
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser
from account.serializers import AddExistUserSerializer
from common.filters import FieldSearchFilter
from hierarchy.models import Department
from navigation.models import group_table
from .models import HomeGroup, Church
from .serializers import (
    ChurchSerializer, ChurchListSerializer,
    HomeGroupSerializer, HomeGroupDetailSerializer, HomeGroupListSerializer, GroupUserSerializer)


class PaginationMixin(PageNumberPagination):
    category = None
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        assert self.category is not None, 'Not Category selected'
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'table_columns': group_table(self.request.user, self.category),
            'results': data,
        })


class ChurchPagination(PaginationMixin):
    category = 'churches'


class HomeGroupPagination(PaginationMixin):
    category = 'home_groups'


class GroupUsersPagination(PaginationMixin):
    category = 'group_users'


class ChurchFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(name='department', queryset=Department.objects.all())
    pastor = django_filters.ModelChoiceFilter(name='pastor', queryset=CustomUser.objects.filter(
        hierarchy__level__gt=1))

    class Meta:
        model = Church
        fields = ['department', 'pastor', 'title', 'country', 'city', 'is_open', 'phone_number',]


class ChurchViewSet(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):

    queryset = Church.objects.all()

    serializer_class = ChurchSerializer
    serializer_list_class = ChurchListSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)

    ordering_fields = ('title', 'city', 'department', 'home_group', 'is_open', 'opening_date',
                       'pastor', 'phone_number', 'address',)

    filter_class = ChurchFilter
    field_search_fields = {
        'search_title': ('title',),
        'search_department': ('department__title',),
        'search_pastor': ('pastor__last_name', 'pastor__first_name', 'pastor__middle_name'),
        'search_country': ('country',),
        'search_city': ('city',),
    }
    permission_classes = (IsAuthenticated,)
    pagination_class = ChurchPagination

    def get_serializer_class(self):
        if self.action in 'list':
            return self.serializer_list_class
        return self.serializer_class

    def get_queryset(self):
        if self.action in 'list':
            return self.queryset.annotate(
                count_groups=Count('home_group', distinct=True),
                count_users=Count('users', distinct=True) + Count('home_group__users', distinct=True))
        return self.queryset

    @detail_route(methods=['get'], pagination_class=GroupUsersPagination)
    def all_users(self, request, pk):
        church = self.get_object()
        all_users = CustomUser.objects.filter(Q(churches=church) | Q(home_groups__in=church.home_group.all()))
        page = self.paginate_queryset(all_users)
        serializer = GroupUserSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @detail_route(methods=['get'], pagination_class=HomeGroupPagination)
    def home_groups(self, request, pk):
        serializer = HomeGroupListSerializer
        church = self.get_object()
        queryset = HomeGroup.objects.filter(church__id=pk)
        serializer = serializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        serializers = HomeGroupListSerializer(page, many=True)
        return self.get_paginated_response(serializers.data)

    @detail_route(methods=['get'], pagination_class=GroupUsersPagination)
    def users(self, request, pk):
        serializer = GroupUserSerializer
        church = self.get_object()
        queryset = church.users
        serializer = serializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        serializers = GroupUserSerializer(page, many=True)
        return self.get_paginated_response(serializers.data)

    @list_route(methods=['get'])
    def potential_users_church(self, request):
        params = request.query_params
        search = params.get('search', '').strip()
        if len(search) < 3:
            return Response({'search': _('Length of search query must be > 2')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddExistUserSerializer

        users = CustomUser.objects.filter(Q(home_groups__isnull=True) & Q(churches__isnull=True)).annotate(
            full_name=Concat('last_name', V(' '), 'first_name', V(' '), 'middle_name'))
        for s in map(lambda s: s.strip(), search.split(' ')):
            users = users.filter(Q(first_name__istartswith=s) |
                                 Q(last_name__istartswith=s) |
                                 Q(middle_name__istartswith=s))

        department_id = params.get('department', None)
        if department_id is not None:
            users = users.filter(department_id=department_id)

        serializers = serializer(users[:30], many=True)

        return Response(serializers.data)

    @detail_route(methods=['get'])
    def potential_users_group(self, request, pk):
        params = request.query_params
        search = params.get('search', '').strip()
        if len(search) < 3:
            return Response({'search': _('Length of search query must be > 2')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddExistUserSerializer

        users = CustomUser.objects. \
            filter(Q(home_groups__isnull=True) & (Q(churches__isnull=True) | Q(churches__id=pk))). \
            annotate(full_name=Concat('last_name', V(' '), 'first_name', V(' '), 'middle_name'))
        for s in map(lambda s: s.strip(), search.split(' ')):
            users = users.filter(Q(first_name__istartswith=s) |
                                 Q(last_name__istartswith=s) |
                                 Q(middle_name__istartswith=s))

        department_id = params.get('department', None)
        if department_id is not None:
            users = users.filter(department_id=department_id)

        serializers = serializer(users[:30], many=True)

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
        user_id = request.data.get('user_id')
        church = self.get_object()

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

    # Helpers

    @staticmethod
    def filter_potential_users_for_group(qs, pk):
        return qs.filter(Q(home_groups__isnull=True) & (Q(churches__isnull=True) | Q(churches__id=pk)))

    @staticmethod
    def filter_potential_users_for_church(qs):
        return qs.filter(Q(home_groups__isnull=True) & Q(churches__isnull=True))

    @staticmethod
    def _get_potential_users(request, filter, *args):
        params = request.query_params
        search = params.get('search', '').strip()
        if len(search) < 3:
            return Response({'search': _('Length of search query must be > 2')}, status=status.HTTP_400_BAD_REQUEST)

        users = filter(*args).annotate(full_name=Concat('last_name', V(' '), 'first_name', V(' '), 'middle_name'))

        search_queries = map(lambda s: s.strip(), search.split(' '))
        for s in search_queries:
            users = users.filter(
                Q(first_name__istartswith=s) | Q(last_name__istartswith=s) | Q(middle_name__istartswith=s) |
                Q(search_name__icontains=s)
            )

        department_id = params.get('department', None)
        if department_id is not None:
            users = users.filter(department_id=department_id)

        serializers = AddExistUserSerializer(users[:30], many=True)

        return Response(serializers.data)


class HomeGroupFilter(django_filters.FilterSet):
    church = django_filters.ModelChoiceFilter(name='church', queryset=Church.objects.all())
    leader = django_filters.ModelChoiceFilter(name='leader', queryset=CustomUser.objects.filter(
        hierarchy__level__gt=0))

    class Meta:
        model = HomeGroup
        fields = ['church', 'leader', 'title', 'city', 'phone_number', 'website']


class HomeGroupViewSet(mixins.UpdateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin,
                       viewsets.GenericViewSet):

    queryset = HomeGroup.objects.all()

    serializer_class = HomeGroupSerializer
    serializer_list_class = HomeGroupListSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,)

    ordering_fields = ('title', 'church', 'city', 'leader', 'opening_date', 'phone_number',)

    filter_class = HomeGroupFilter
    field_search_fields = {
        'search_title': ('title',),
        'search_church': ('church__title',),
        'search_leader': ('leader__last_name', 'leader__first_name', 'leader__middle_name'),
        'search_city': ('city',),
    }
    permission_classes = (IsAuthenticated,)
    pagination_class = HomeGroupPagination

    def get_serializer_class(self):
        if self.action in 'list':
            return self.serializer_list_class
        return self.serializer_class

    @detail_route(methods=['get'], pagination_class=GroupUsersPagination)
    def users(self, request, pk):
        serializer = GroupUserSerializer
        home_group = self.get_object()
        queryset = home_group.users
        serializer = serializer(queryset, many=True)
        page = self.paginate_queryset(serializer.data)
        serializers = GroupUserSerializer(page, many=True)
        return self.get_paginated_response(serializers.data)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data.get('user_id')
        home_group = self.get_object()
        church = home_group.church

        if not user_id:
            return Response({"message": "Некоректные данные"},
                            status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(id=user_id)
        if not user.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данного пользователя не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = user.get()
        if user.home_groups.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Данный пользователь уже состоит в Домашней Группе.'},
                            status=status.HTTP_400_BAD_REQUEST)

        """
        if not user.churches.exists():
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Пользователь не состоит в Церкви'},
                            status=status.HTTP_400_BAD_REQUEST)
        """

        if user.churches.exists() and user.churches.get().id != church.id:
            return Response({'message': 'Невозможно добавить пользователя. '
                                        'Пользователь является членом другой Церкви'},
                            status=status.HTTP_400_BAD_REQUEST)

        if church.users.filter(id=user_id).exists():
            church.users.remove(user_id)

        home_group.users.add(user_id)
        return Response({'message': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data.get('user_id')
        home_group = self.get_object()
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
