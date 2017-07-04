# -*- coding: utf-8
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Case, When, BooleanField
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import status, exceptions, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser
from account.serializers import AddExistUserSerializer
from common.filters import FieldSearchFilter
from common.test_helpers.utils import get_real_user
from common.views_mixins import ExportViewSetMixin, ModelWithoutDeleteViewSet
from group.filters import (HomeGroupFilter, ChurchFilter, FilterChurchMasterTree, FilterHomeGroupMasterTree,
                           HomeGroupsDepartmentFilter)
from group.pagination import ChurchPagination, HomeGroupPagination
from group.resources import ChurchResource, HomeGroupResource
from group.views_mixins import (ChurchUsersMixin, HomeGroupUsersMixin, ChurchHomeGroupMixin)
from .models import HomeGroup, Church
from .serializers import (ChurchSerializer, ChurchListSerializer, HomeGroupSerializer,
                          HomeGroupListSerializer, ChurchStatsSerializer, UserNameSerializer,
                          AllHomeGroupsListSerializer, HomeGroupStatsSerializer, ChurchWithoutPaginationSerializer,
                          ChurchDashboardSerializer
                          )


class ChurchViewSet(ModelWithoutDeleteViewSet, ChurchUsersMixin,
                    ChurchHomeGroupMixin, ExportViewSetMixin):
    queryset = Church.objects.all()

    serializer_class = ChurchSerializer
    serializer_list_class = ChurchListSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = ChurchPagination

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       FilterChurchMasterTree,
                       )

    ordering_fields = ('title', 'city', 'department__title', 'home_group',
                       'is_open', 'opening_date', 'pastor__last_name', 'phone_number',
                       'address', 'website', 'count_groups', 'count_users', 'country')

    filter_class = ChurchFilter

    field_search_fields = {
        'search_title': ('title', 'pastor__last_name', 'pastor__first_name', 'pastor__middle_name'),
    }

    resource_class = ChurchResource

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.for_user(self.request.user).annotate(
                count_groups=Count('home_group', distinct=True),
                count_users=Count('uusers', distinct=True) + Count(
                    'home_group__uusers', distinct=True))
        return self.queryset.for_user(self.request.user)

    @list_route(methods=['GET'], serializer_class=UserNameSerializer)
    def available_pastors(self, request):
        department_id = request.query_params.get('department_id')
        master_tree_id = request.query_params.get('master_tree')

        master = self._get_master(request.user, master_tree_id)

        pastors = master.get_descendants(include_self=True).filter(hierarchy__level__gte=2)
        if department_id:
            pastors = pastors.filter(departments=department_id)

        pastors = self.serializer_class(pastors, many=True)
        return Response(pastors.data)

    @list_route(methods=['get'])
    def potential_users_church(self, request):
        users = CustomUser.objects.all()
        return self._get_potential_users(request, self.filter_potential_users_for_church, users)

    @detail_route(methods=['get'])
    def potential_users_group(self, request, pk):
        users = CustomUser.objects.all()
        return self._get_potential_users(request, self.filter_potential_users_for_group, users, pk)

    @detail_route(methods=['post', 'put'])
    def add_user(self, request, pk):
        # TODO filter by perm
        church = get_object_or_404(Church, pk=pk)
        user = self._get_user(request.data.get('user_id', None))

        self._validate_user_for_add_user(user)
        user.set_church_and_log(church, get_real_user(request))

        return Response({'detail': _('Пользователь успешно добавлен.')},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data.get('user_id')
        church = self.get_object()

        user = self._get_user(user_id)

        if user.cchurch != church:
            if user.hhome_group:
                raise exceptions.ValidationError({
                    'home_groups': [{'id': user.hhome_group.id, 'name': user.hhome_group.get_title}],
                    'detail': _('Пожалуйста, удалите сначала пользователя из домашней группы.')
                })
            raise exceptions.ValidationError({
                'detail': _('Невозможно удалить пользователя.'
                            'Пользователь не принадлежит к данной Церкви.')
            })

        user.set_church_and_log(None, get_real_user(request))
        return Response({'detail': _('Пользователь успешно удален из Церкви')},
                        status=status.HTTP_204_NO_CONTENT)

    @detail_route(methods=['GET'])
    def statistics(self, request, pk):
        stats = {}
        church = get_object_or_404(Church, pk=pk)

        stats['church_users'] = church.uusers.count()

        stats['church_all_users'] = (church.uusers.count() + HomeGroup.objects.filter(
            church_id=pk).aggregate(home_users=Count('uusers'))['home_users'])

        stats['parishioners_count'] = church.uusers.filter(hierarchy__level=0).count() + HomeGroup.objects.filter(
            church__id=pk).filter(uusers__hierarchy__level=0).count()

        stats['leaders_count'] = church.uusers.filter(hierarchy__level=1).count() + HomeGroup.objects.filter(
            church__id=pk).filter(uusers__hierarchy__level=1).count()

        stats['home_groups_count'] = church.home_group.count()

        stats['fathers_count'] = (church.uusers.filter(spiritual_level=CustomUser.FATHER).count() +
                                  HomeGroup.objects.filter(church__id=pk).filter(
                                      uusers__spiritual_level=3).count())

        stats['juniors_count'] = (church.uusers.filter(spiritual_level=CustomUser.JUNIOR).count() +
                                  HomeGroup.objects.filter(church__id=pk).filter(
                                      uusers__spiritual_level=2).count())

        stats['babies_count'] = (church.uusers.filter(spiritual_level=CustomUser.BABY).count() +
                                 HomeGroup.objects.filter(church__id=pk).filter(
                                     uusers__spiritual_level=1).count())

        stats['partners_count'] = church.uusers.filter(partnership__is_active=True).count() + HomeGroup.objects.filter(
            church__id=pk).filter(uusers__partnership__is_active=True).count()

        serializer = ChurchStatsSerializer
        stats = serializer(stats)
        return Response(stats.data)

    @list_route(methods=['GET'], serializer_class=ChurchWithoutPaginationSerializer, pagination_class=None)
    def for_select(self, request):
        if not request.query_params.get('department'):
            raise exceptions.ValidationError({'detail': _("Некорректный запрос. Департамент не передан.")})

        departments = request.query_params.getlist('department')

        churches = Church.objects.filter(department__in=departments)
        churches = self.serializer_class(churches, many=True)
        return Response(churches.data)

    # Helpers

    @staticmethod
    def _get_master(master, master_tree_id):
        if not master_tree_id:
            return master
        try:
            return master.get_descendants(include_self=True).filter(hierarchy__level__gte=2).get(pk=master_tree_id)
        except ValueError:
            raise exceptions.ValidationError({'detail': _("master_tree_id is incorrect.")})
        except ObjectDoesNotExist:
            raise exceptions.ValidationError({'detail': _("You are don't have permissions for filter by this master.")})

    @staticmethod
    def _get_user(user_id=None):
        if not user_id:
            raise exceptions.ValidationError({'detail': _('"user_id" is required.')})
        try:
            user = get_object_or_404(CustomUser, pk=user_id)
        except Http404:
            raise exceptions.ValidationError({'detail': _('User with id = %s does not exist.' % user_id)})
        return user

    @staticmethod
    def filter_potential_users_for_group(qs, pk):
        return qs.annotate(can_add=Case(When(Q(hhome_group__isnull=True) & (Q(
            cchurch__isnull=True) | Q(cchurch_id=pk)), then=True), default=False, output_field=BooleanField()))

    @staticmethod
    def filter_potential_users_for_church(qs):
        return qs.annotate(can_add=Case(When(Q(hhome_group__isnull=True) & Q(
            cchurch__isnull=True), then=True), default=False, output_field=BooleanField()))

    @staticmethod
    def _get_potential_users(request, filter, *args):
        params = request.query_params
        search = params.get('search', '').strip()
        if len(search) < 3:
            return Response({'search': _('Length of search query must be > 2')},
                            status=status.HTTP_400_BAD_REQUEST)

        users = filter(*args).annotate(full_name=Concat(
            'last_name', V(' '), 'first_name', V(' '), 'middle_name'))

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
    def _validate_user_for_add_user(user):
        if user.cchurch:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно добавить пользователя, данный пользователь уже состоит в Церкви.')})

        if user.hhome_group:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно добавить пользователя, данный пользователь уже состоит в Домашней Группе.')})

    @list_route(methods=['GET'], serializer_class=ChurchDashboardSerializer)
    def dashboard_counts(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            user = get_object_or_404(CustomUser, pk=user_id)
        else:
            user = self.request.user

        queryset = self.queryset.for_user(user)
        result = queryset.aggregate(
            peoples_in_churches=Count('uusers', distinct=True),
            peoples_in_home_groups=Count('home_group__uusers', distinct=True))
        result['churches_count'] = queryset.count()
        result['home_groups_count'] = HomeGroup.objects.for_user(user).count()

        result = self.serializer_class(result)
        return Response(result.data)


class HomeGroupViewSet(ModelWithoutDeleteViewSet, HomeGroupUsersMixin, ExportViewSetMixin):
    queryset = HomeGroup.objects.all()

    serializer_class = HomeGroupSerializer
    serializer_list_class = HomeGroupListSerializer

    permission_classes = (IsAuthenticated,)
    pagination_class = HomeGroupPagination

    filter_backends = (filters.DjangoFilterBackend,
                       FieldSearchFilter,
                       filters.OrderingFilter,
                       FilterHomeGroupMasterTree,
                       HomeGroupsDepartmentFilter)

    ordering_fields = ('title', 'church', 'leader__last_name', 'city', 'leader',
                       'address', 'opening_date', 'phone_number', 'website',
                       'department', 'count_users')

    filter_class = HomeGroupFilter

    field_search_fields = {
        'search_title': ('title', 'leader__last_name', 'leader__first_name', 'leader__middle_name')
    }

    resource_class = HomeGroupResource

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return self.serializer_list_class
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'list':
            return self.queryset.for_user(self.request.user).annotate(count_users=Count('uusers'))
        return self.queryset.for_user(self.request.user)

    @detail_route(methods=['post'])
    def add_user(self, request, pk):
        home_group = get_object_or_404(HomeGroup, pk=pk)
        user = self._get_user(request.data.get('user_id', None))

        self._validate_user_for_add_user(user, home_group)
        user.set_home_group_and_log(home_group, get_real_user(request))

        return Response({'detail': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data.get('user_id', None)
        home_group = get_object_or_404(HomeGroup, pk=pk)
        user = self._get_user(user_id)

        self._validate_user_for_del_user(user, home_group)

        user.del_home_group_and_log(get_real_user(request))

        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['GET'], serializer_class=UserNameSerializer)
    def available_leaders(self, request):
        church_id = request.query_params.get('church_id')
        department_id = request.query_params.get('department_id')
        master_tree_id = request.query_params.get('master_tree')

        master = self._get_master(request.user, master_tree_id)

        leaders = master.get_descendants(include_self=True).filter(hierarchy__level__gte=1)
        if church_id:
            leaders = leaders.filter(Q(hhome_group__church_id=church_id) | Q(cchurch_id=church_id))
        if department_id:
            leaders = leaders.filter(departments=department_id)

        leaders = self.serializer_class(leaders, many=True)
        return Response(leaders.data)

    @detail_route(methods=["GET"])
    def statistics(self, request, pk):
        stats = {}
        home_group = get_object_or_404(HomeGroup, pk=pk)

        stats['users_count'] = home_group.uusers.count()
        stats['fathers_count'] = home_group.uusers.filter(spiritual_level=CustomUser.FATHER).count()
        stats['juniors_count'] = home_group.uusers.filter(spiritual_level=CustomUser.JUNIOR).count()
        stats['babies_count'] = home_group.uusers.filter(spiritual_level=CustomUser.BABY).count()
        stats['partners_count'] = home_group.uusers.filter(partnership__is_active=True).count()

        serializer = HomeGroupStatsSerializer
        stats = serializer(stats)
        return Response(stats.data)

    @list_route(methods=['GET'], serializer_class=AllHomeGroupsListSerializer)
    def for_select(self, request):
        church_id = request.query_params.get('church_id')

        if not church_id:
            raise exceptions.ValidationError({'detail': _("Некорректный запрос. Церковь не передана.")})

        home_groups = HomeGroup.objects.filter(church_id=church_id)
        home_groups = self.serializer_class(home_groups, many=True)

        return Response(home_groups.data)

    # Helpers

    @staticmethod
    def _get_master(master, master_tree_id):
        if not master_tree_id:
            return master
        try:
            return master.get_descendants(include_self=True).filter(hierarchy__level__gte=1).get(pk=master_tree_id)
        except ValueError:
            raise exceptions.ValidationError({'detail': _("master_tree_id is incorrect.")})
        except ObjectDoesNotExist:
            raise exceptions.ValidationError({'detail': _("You are don't have permissions for filter by this master.")})

    @staticmethod
    def _get_user(user_id=None):
        if not user_id:
            raise exceptions.ValidationError({'detail': _('"user_id" is required.')})
        try:
            user = get_object_or_404(CustomUser, pk=user_id)
        except Http404:
            raise exceptions.ValidationError({'detail': _('User with id = %s does not exist.' % user_id)})
        return user

    @staticmethod
    def _validate_user_for_add_user(user, home_group):
        if user.hhome_group:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно добавить пользователя, данный пользователь уже состоит в Домашней Группе.')})

        if user.cchurch and user.cchurch != home_group.church:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно добавить пользователя, пользователь является членом другой Церкви')})

    @staticmethod
    def _validate_user_for_del_user(user, home_group):
        if user.hhome_group != home_group:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно удалить пользователя.'
                             'Пользователь не принадлежит к данной Домашней Группе.')})
