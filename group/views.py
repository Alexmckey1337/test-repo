# -*- coding: utf-8
from django.db.models import Count
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, exceptions, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser
from account.serializers import AddExistUserSerializer
from common.filters import FieldSearchFilter
from common.views_mixins import ExportViewSetMixin, ModelWithoutDeleteViewSet
from group.filters import HomeGroupFilter, ChurchFilter, FilterChurchMasterTree, FilterHomeGroupMasterTree
from group.pagination import ChurchPagination, HomeGroupPagination
from group.resources import ChurchResource, HomeGroupResource
from group.views_mixins import (
    ChurchUsersMixin, HomeGroupUsersMixin, ChurchHomeGroupMixin)
from hierarchy.models import Department
from .models import HomeGroup, Church
from .serializers import (ChurchSerializer, ChurchListSerializer, HomeGroupSerializer, HomeGroupListSerializer,
                          ChurchStatsSerializer, HomeGroupStatsSerializer, AllChurchesListSerializer,
                          AllHomeGroupsListSerializer, PastorNameSerializer, LeaderNameSerializer)


class ChurchViewSet(ModelWithoutDeleteViewSet, ChurchUsersMixin, ChurchHomeGroupMixin, ExportViewSetMixin):
    queryset = Church.objects.all()

    serializer_class = ChurchSerializer
    serializer_list_class = ChurchListSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       FilterChurchMasterTree,
                       )

    ordering_fields = ('title', 'city', 'department__title', 'home_group', 'is_open', 'opening_date',
                       'pastor__last_name', 'phone_number', 'address', 'website', 'count_groups',
                       'count_users', 'country')

    filter_class = ChurchFilter
    field_search_fields = {
        'search_title': ('title',),
    }

    permission_classes = (IsAuthenticated,)
    pagination_class = ChurchPagination
    resource_class = ChurchResource

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(
                count_groups=Count('home_group', distinct=True),
                count_users=Count('users', distinct=True) + Count('home_group__users', distinct=True))
        return self.queryset

    @list_route(methods=['get'])
    def potential_users_church(self, request):
        users = CustomUser.objects.all()
        return self._get_potential_users(request, self.filter_potential_users_for_church, users)

    @detail_route(methods=['get'])
    def potential_users_group(self, request, pk):
        users = CustomUser.objects.all()
        return self._get_potential_users(request, self.filter_potential_users_for_group, users, pk)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data.get('user_id')
        church = self.get_object()

        self._validate_user_for_add_user(user_id)

        church.users.add(user_id)
        return Response({'message': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data.get('user_id')
        church = self.get_object()

        self._validate_user_for_del_user(user_id, church)

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
                Q(first_name__istartswith=s) | Q(last_name__istartswith=s) |
                Q(middle_name__istartswith=s) | Q(search_name__icontains=s))

        department_id = params.get('department', None)
        if department_id is not None:
            users = users.filter(departments__id=department_id)

        serializers = AddExistUserSerializer(users[:30], many=True)

        return Response(serializers.data)

    @staticmethod
    def _validate_user_for_add_user(user_id):
        if not user_id:
            raise exceptions.ValidationError("Некоректные данные")
        user = CustomUser.objects.filter(id=user_id)
        if not user.exists():
            raise exceptions.ValidationError(
                _('Невозможно добавить пользователя. Данного пользователя не существует.'))
        user = user.get()
        if user.churches.exists():
            raise exceptions.ValidationError(
                _('Невозможно добавить пользователя. Данный пользователь уже состоит в Церкви.'))
        if user.home_groups.exists():
            raise exceptions.ValidationError(
                _('Невозможно добавить пользователя. Данный пользователь уже состоит в Домашней Группе.'))

    @staticmethod
    def _validate_user_for_del_user(user_id, church):
        if not user_id:
            raise exceptions.ValidationError("Некоректные данные")
        if not CustomUser.objects.filter(id=user_id).exists():
            raise exceptions.ValidationError(
                _('Невозможно удалить пользователя. Данного пользователя не существует.'))
        if not church.users.filter(id=user_id).exists():
            raise exceptions.ValidationError(
                _('Невозможно удалить пользователя. Пользователь не принадлежит к данной Церкви.'))

    @detail_route(methods=['GET'])
    def statistics(self, request, pk):
        stats = {}
        church = get_object_or_404(Church, pk=pk)
        stats['church_users'] = church.users.count()
        stats['church_all_users'] = (church.users.count() + HomeGroup.objects.filter(church_id=pk).aggregate(
            home_users=Count('users'))['home_users'])
        stats['parishioners_count'] = church.users.filter(hierarchy__level=0).count() + HomeGroup.objects.filter(
            church__id=pk).filter(users__hierarchy__level=0).count()
        stats['leaders_count'] = church.users.filter(hierarchy__level=1).count() + HomeGroup.objects.filter(
            church__id=pk).filter(users__hierarchy__level=1).count()
        stats['home_groups_count'] = church.home_group.count()
        stats['fathers_count'] = church.users.filter(spiritual_level=CustomUser.FATHER).count() + \
                                 HomeGroup.objects.filter(church__id=pk).filter(users__spiritual_level=3).count()
        stats['juniors_count'] = church.users.filter(spiritual_level=CustomUser.JUNIOR).count() + \
                                 HomeGroup.objects.filter(church__id=pk).filter(users__spiritual_level=2).count()
        stats['babies_count'] = church.users.filter(spiritual_level=CustomUser.BABY).count() + \
                                HomeGroup.objects.filter(church__id=pk).filter(users__spiritual_level=1).count()
        stats['partners_count'] = church.users.filter(partnership__is_active=True).count() + HomeGroup.objects.filter(
            church__id=pk).filter(users__partnership__is_active=True).count()

        serializer = ChurchStatsSerializer
        stats = serializer(stats)
        return Response(stats.data)

    @list_route(methods=['GET'], serializer_class=AllChurchesListSerializer)
    def all(self, request):
        all_churches = self.serializer_class(Church.objects.all(), many=True)
        return Response(all_churches.data)

    @list_route(methods=['GET'], serializer_class=PastorNameSerializer)
    def get_pastors_by_department(self, request):
        department_id = request.query_params.get('department_id')

        if not Department.objects.filter(id=department_id).exists():
            raise exceptions.ValidationError(_('Отдела с id=%s не существует.' % department_id))

        pastors = CustomUser.objects.filter(church__pastor__id__isnull=False).filter(
            church__department__id=department_id).distinct()

        pastors = self.serializer_class(pastors, many=True)
        return Response(pastors.data)


class HomeGroupViewSet(ModelWithoutDeleteViewSet, HomeGroupUsersMixin, ExportViewSetMixin):
    queryset = HomeGroup.objects.all()

    serializer_class = HomeGroupSerializer
    serializer_list_class = HomeGroupListSerializer

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       FilterHomeGroupMasterTree,
                       )

    ordering_fields = ('title', 'church', 'leader__last_name', 'city', 'leader', 'address', 'opening_date',
                       'phone_number', 'website', 'department', 'count_users')

    filter_class = HomeGroupFilter
    field_search_fields = {
        'search_title': ('title',)
    }

    permission_classes = (IsAuthenticated,)
    pagination_class = HomeGroupPagination
    resource_class = HomeGroupResource

    def get_serializer_class(self):
        if self.action in 'list':
            return self.serializer_list_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.annotate(count_users=Count('users'))
        return self.queryset

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        user_id = request.data.get('user_id')
        home_group = get_object_or_404(HomeGroup, pk=pk)
        church = home_group.church

        self._validate_user_for_add_user(user_id, church)

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

        self._validate_user_for_del_user(user_id, home_group)

        home_group.users.remove(user_id)
        church.users.add(user_id)
        return Response({'message': 'Пользователь успешно удален.'},
                        status=status.HTTP_204_NO_CONTENT)

    # Helpers

    @staticmethod
    def _validate_user_for_add_user(user_id, church):
        if not user_id:
            raise exceptions.ValidationError(_("Некоректные данные"))

        user = CustomUser.objects.filter(id=user_id)
        if not user.exists():
            raise exceptions.ValidationError(
                _('Невозможно добавить пользователя. Данного пользователя не существует.'))

        user = user.get()
        if user.home_groups.exists():
            raise exceptions.ValidationError(
                _('Невозможно добавить пользователя. Данный пользователь уже состоит в Домашней Группе.'))

        if user.churches.exists() and user.churches.get().id != church.id:
            raise exceptions.ValidationError(
                _('Невозможно добавить пользователя. Пользователь является членом другой Церкви'))

    @staticmethod
    def _validate_user_for_del_user(user_id, home_group):
        if not user_id:
            raise exceptions.ValidationError(_("Некоректные данные"))

        if not CustomUser.objects.filter(id=user_id).exists():
            raise exceptions.ValidationError(
                _('Невозможно удалить пользователя. Данного пользователя не существует.'))

        if not home_group.users.filter(id=user_id).exists():
            raise exceptions.ValidationError(
                _('Невозможно удалить пользователя. Пользователь не принадлежит к данной Домашней Группе.'))

    @detail_route(methods=["GET"])
    def statistics(self, request, pk):
        stats = {}
        home_group = get_object_or_404(HomeGroup, pk=pk)
        stats['users_count'] = home_group.users.count()
        stats['fathers_count'] = home_group.users.filter(spiritual_level=CustomUser.FATHER).count()
        stats['juniors_count'] = home_group.users.filter(spiritual_level=CustomUser.JUNIOR).count()
        stats['babies_count'] = home_group.users.filter(spiritual_level=CustomUser.BABY).count()
        stats['partners_count'] = home_group.users.filter(partnership__is_active=True).count()

        serializer = HomeGroupStatsSerializer
        stats = serializer(stats)
        return Response(stats.data)

    @list_route(methods=['GET'], serializer_class=AllHomeGroupsListSerializer)
    def all(self, request):
        all_home_groups = self.serializer_class(HomeGroup.objects.all(), many=True)
        return Response(all_home_groups.data)

    @list_route(methods=['GET'], serializer_class=LeaderNameSerializer)
    def get_leaders_by_church(self, request):
        church_id = request.query_params.get('church_id')

        if not Church.objects.filter(id=church_id).exists():
            raise exceptions.ValidationError(_('Церкви с id=%s не существует.' % church_id))

        leaders = CustomUser.objects.filter(home_group__leader__id__isnull=False).filter(
            home_group__church__id=church_id).distinct()

        leaders = self.serializer_class(leaders, many=True)
        return Response(leaders.data)
