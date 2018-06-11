import logging
from datetime import datetime
from itertools import chain

import pytz
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Case, When, BooleanField
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.http import Http404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_framework import status, exceptions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.account.api.serializers import AddExistUserSerializer
from apps.account.models import CustomUser
from apps.analytics.mixins import LogAndCreateUpdateDestroyMixin
from apps.event.models import ChurchReport, Meeting, MeetingType
from apps.group.api.filters import (
    HomeGroupFilter, ChurchFilter, FilterChurchMasterTree, FilterHomeGroupMasterTree,
    HomeGroupsDepartmentFilter, FilterHGLeadersByMasterTree, FilterHGLeadersByChurch,
    FilterHGLeadersByDepartment, FilterPotentialHGLeadersByMasterTree,
    FilterPotentialHGLeadersByChurch, FilterPotentialHGLeadersByDepartment, VoHomeGroupsDepartmentFilter)
from apps.group.api.pagination import (
    ForSelectPagination, PotentialUsersPagination)
from apps.group.api.permissions import (
    CanSeeChurch, CanCreateChurch, CanEditChurch, CanExportChurch,
    CanSeeHomeGroup, CanCreateHomeGroup, CanEditHomeGroup, CanExportHomeGroup, VoCanSeeHomeGroup, VoCanSeeDirection)
from apps.group.api.serializers import (
    ChurchSerializer, ChurchTableSerializer, HomeGroupSerializer,
    HomeGroupListSerializer, ChurchStatsSerializer, UserNameSerializer,
    AllHomeGroupsListSerializer, HomeGroupStatsSerializer, ChurchWithoutPaginationSerializer,
    ChurchDashboardSerializer, ChurchReadSerializer, HomeGroupReadSerializer, ChurchLocationSerializer,
    HomeGroupLocationSerializer, VoHGSerializer, VoDirectionSerializer)
from apps.group.api.views_mixins import (ChurchUsersMixin, HomeGroupUsersMixin, ChurchHomeGroupMixin, LocationMixin)
from apps.group.models import HomeGroup, Church, Direction
from apps.group.resources import ChurchResource, HomeGroupResource
from apps.location.models import City
from common.filters import FieldSearchFilter, OrderingFilterWithPk
from common.test_helpers.utils import get_real_user
from common.views_mixins import ExportViewSetMixin, TableViewMixin, ModelWithoutListViewSet
from common.week_range import week_range

logger = logging.getLogger(__name__)


class ChurchTableView(TableViewMixin):
    table_name = 'church'

    queryset = Church.objects.select_related('pastor', 'department', 'locality').order_by('title', 'pk')
    serializer_class = ChurchTableSerializer
    permission_classes = (CanSeeChurch,)

    filter_backends = (
        rest_framework.DjangoFilterBackend,
        FieldSearchFilter,
        OrderingFilterWithPk,
        FilterChurchMasterTree,
    )
    ordering_fields = (
        'title', 'city', 'department__title', 'home_group',
        'is_open', 'opening_date', 'pastor__last_name', 'phone_number',
        'address', 'website', 'count_groups', 'count_users', 'country', 'region'
    )
    field_search_fields = {
        'search_title': ('title', 'pastor__last_name', 'pastor__first_name', 'pastor__middle_name', 'city'),
    }
    filter_class = ChurchFilter

    def get(self, request, *args, **kwargs):
        """
        Getting list of churches for table


        By default ordering by ``title``.
        Pagination by 30 churches per page.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.for_user(self.request.user)


class ChurchExportView(ChurchTableView, ExportViewSetMixin):
    permission_classes = (IsAuthenticated, CanExportChurch)
    resource_class = ChurchResource

    def post(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class ChurchLocationListView(LocationMixin, ChurchTableView):
    serializer_class = ChurchLocationSerializer


class ChurchViewSet(LogAndCreateUpdateDestroyMixin, ModelWithoutListViewSet, ChurchUsersMixin,
                    ChurchHomeGroupMixin):
    queryset = Church.objects.all()
    ordering_fields = ()

    serializer_class = ChurchSerializer
    serializer_read_class = ChurchReadSerializer

    permission_classes = (IsAuthenticated,)
    permission_retrieve_classes = (IsAuthenticated, CanSeeChurch)
    permission_create_classes = (IsAuthenticated, CanCreateChurch)
    permission_update_classes = (IsAuthenticated, CanEditChurch)
    permission_partial_update_classes = permission_update_classes

    def get_permissions(self):
        permission_classes = getattr(self, 'permission_{}_classes'.format(self.action), self.permission_classes)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.serializer_read_class
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.for_user(self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.churchreport_set.exists():
            raise exceptions.ValidationError({'message': _('Невозможно удалить церковь. '
                                                           'На данную церковь есть созданные отчеты.')})
        if instance.home_group.exists():
            raise exceptions.ValidationError({'message': _('Невозможно удалить церковь. '
                                                           'В составе данной церкви есть Домашняя Группа.')})
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], serializer_class=UserNameSerializer)
    def available_pastors(self, request):
        department_id = request.query_params.get('department_id')
        master_tree_id = request.query_params.get('master_tree')

        master = self._get_master(request.user, master_tree_id)

        if (request.user.is_staff and not master_tree_id) or request.user.is_staff:
            pastors = CustomUser.objects.filter(hierarchy__level__gte=2)
        else:
            pastors = master.__class__.get_tree(master).filter(hierarchy__level__gte=2)
        if department_id:
            pastors = pastors.filter(departments=department_id)

        pastors = self.serializer_class(pastors, many=True)
        return Response(pastors.data)

    @action(detail=False, methods=['get'], pagination_class=PotentialUsersPagination)
    def potential_users_church(self, request):
        users = CustomUser.objects.all()
        return self._get_potential_users(request, self.filter_potential_users_for_church, users)

    @action(detail=True, methods=['get'], pagination_class=PotentialUsersPagination)
    def potential_users_group(self, request, pk):
        users = CustomUser.objects.all()
        return self._get_potential_users(request, self.filter_potential_users_for_group, users, pk)

    @action(detail=True, methods=['post', 'put'])
    def add_user(self, request, pk):
        church = get_object_or_404(Church, pk=pk)
        user = self._get_user(request.data.get('user_id', None))

        request.user.can_add_user_to_church(user, church)
        self._validate_user_for_add_user(user)

        user.set_church_and_log(church, get_real_user(request))

        return Response({'detail': _('Пользователь успешно добавлен.')},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data.get('user_id')
        church = self.get_object()

        user = self._get_user(user_id)
        request.user.can_del_user_from_church(user, church)

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

    @action(detail=True, methods=['GET'], permission_classes=(CanSeeChurch,))
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
                                  HomeGroup.objects.filter(church_id=pk).filter(
                                      uusers__spiritual_level=3).count())

        stats['juniors_count'] = (church.uusers.filter(spiritual_level=CustomUser.JUNIOR).count() +
                                  HomeGroup.objects.filter(church_id=pk).filter(
                                      uusers__spiritual_level=2).count())

        stats['babies_count'] = (church.uusers.filter(spiritual_level=CustomUser.BABY).count() +
                                 HomeGroup.objects.filter(church_id=pk).filter(
                                     uusers__spiritual_level=1).count())

        stats['partners_count'] = church.uusers.filter(partners__is_active=True).count() + HomeGroup.objects.filter(
            church__id=pk).filter(uusers__partners__is_active=True).count()

        serializer = ChurchStatsSerializer
        stats = serializer(stats)
        return Response(stats.data)

    @action(detail=False, methods=['GET'], serializer_class=ChurchWithoutPaginationSerializer,
            pagination_class=ForSelectPagination)
    def for_select(self, request):
        churches = Church.objects.all()

        department_id = request.query_params.get('department_id')
        if department_id:
            churches = churches.filter(department_id=department_id)

        pastor_id = request.query_params.get('pastor_id')
        if pastor_id:
            churches = churches.filter(pastor_id=pastor_id)

        master_tree = request.query_params.get('master_tree')
        if master_tree:
            churches = churches.for_user(CustomUser.objects.get(id=master_tree))

        churches = self.serializer_class(churches, many=True)
        return Response(churches.data)

    # Helpers

    def _get_master(self, master, master_tree_id):
        if not master_tree_id:
            return master
        try:
            if self.request.user.is_staff:
                return CustomUser.objects.filter(hierarchy__level__gte=2).get(pk=master_tree_id)
            return master.__class__.get_tree(master).filter(hierarchy__level__gte=2).get(pk=master_tree_id)
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

    def filter_potential_users_for_group(self, qs, pk):
        return qs.annotate(
            can_add=Case(
                When(Q(hhome_group__isnull=True) &
                     (Q(cchurch__isnull=True) | Q(cchurch_id=pk)),
                     # & Q(path__startswith=user.path) & Q(depth__gte=user.depth),
                     then=True), default=False, output_field=BooleanField()))

    def filter_potential_users_for_church(self, qs):
        user = self.request.user
        if user.is_staff:
            return qs.annotate(can_add=Case(When(
                Q(hhome_group__isnull=True) & Q(cchurch__isnull=True),
                then=True), default=False, output_field=BooleanField()))
            # & Q(path__startswith=user.path) & Q(depth__gte=user.depth),

        return qs.annotate(can_add=Case(When(
            Q(hhome_group__isnull=True) & Q(cchurch__isnull=True) &
            Q(path__startswith=user.path) & Q(depth__gte=user.depth),
            then=True), default=False, output_field=BooleanField()))

    def _get_potential_users(self, request, filter, *args):
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

        page = self.paginate_queryset(users)
        if page is not None:
            users = AddExistUserSerializer(page, many=True)
            return self.get_paginated_response(users.data)

        users = AddExistUserSerializer(users, many=True)
        return Response(users.data)

    @staticmethod
    def _validate_user_for_add_user(user):
        if user.cchurch:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно добавить пользователя, данный пользователь уже состоит в Церкви.')})

        if user.hhome_group:
            raise exceptions.ValidationError(
                {'detail': _('Невозможно добавить пользователя, данный пользователь уже состоит в Домашней Группе.')})

    @action(detail=False, methods=['GET'], serializer_class=ChurchDashboardSerializer)
    def dashboard_counts(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            user = get_object_or_404(CustomUser, pk=user_id)
        else:
            user = self.request.user

        result = dict()
        result['peoples_in_home_groups'] = CustomUser.objects.for_user(user, extra_perms=False).filter(
            Q(hhome_group__isnull=False)).count()
        result['peoples_in_churches'] = CustomUser.objects.for_user(user, extra_perms=False).filter(
            Q(cchurch__isnull=False) | Q(hhome_group__isnull=False)).count()
        result['churches_count'] = self.queryset.for_user(user, extra_perms=False).count()
        result['home_groups_count'] = HomeGroup.objects.for_user(user, extra_perms=False).count()

        result = self.serializer_class(result)
        return Response(result.data)

    @action(detail=True, methods=['POST'])
    def create_report(self, request, pk):
        church = self.get_object()
        str_date = request.data.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        date = pytz.utc.localize(datetime.strptime(str_date, '%Y-%m-%d'))

        start_week_day, end_week_date = week_range(date)
        start_week_day = start_week_day.strftime('%Y-%m-%d')
        end_week_date = end_week_date.strftime('%Y-%m-%d')

        if ChurchReport.objects.filter(church=church,
                                       date__range=[start_week_day, end_week_date]
                                       ).exists():
            raise exceptions.ValidationError(
                {'message': _('Невозможно создать отчет. '
                              'Для данной церкви на данную неделю есть созданный отчет.')})

        ChurchReport.objects.get_or_create(church=church,
                                           pastor=church.pastor,
                                           date=date,
                                           currency_id=church.report_currency)

        return Response({'message': _('Отчет успешно создан')}, status=status.HTTP_200_OK)


class HomeGroupTableView(TableViewMixin):
    table_name = 'home_group'

    queryset = HomeGroup.objects.select_related('leader', 'church', 'locality').order_by('title', 'pk')
    serializer_class = HomeGroupListSerializer
    permission_classes = (IsAuthenticated, CanSeeHomeGroup)

    filter_backends = (rest_framework.DjangoFilterBackend,
                       FieldSearchFilter,
                       OrderingFilterWithPk,
                       FilterHomeGroupMasterTree,
                       HomeGroupsDepartmentFilter)
    ordering_fields = ('title', 'church', 'leader__last_name', 'city', 'leader',
                       'address', 'opening_date', 'phone_number', 'website',
                       'department', 'count_users')
    field_search_fields = {
        'search_title': ('title', 'leader__last_name', 'leader__first_name', 'leader__middle_name', 'city')
    }
    filter_class = HomeGroupFilter

    def get(self, request, *args, **kwargs):
        """
        Getting list of home groups for table


        By default ordering by ``title``.
        Pagination by 30 groups per page.
        """
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.for_user(self.request.user).annotate(count_users=Count('uusers'))


class HomeGroupExportView(HomeGroupTableView, ExportViewSetMixin):
    permission_classes = (IsAuthenticated, CanExportHomeGroup)
    resource_class = HomeGroupResource

    def post(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.for_user(self.request.user)


class HomeGroupViewSet(LogAndCreateUpdateDestroyMixin, ModelWithoutListViewSet,
                       HomeGroupUsersMixin, ExportViewSetMixin):
    queryset = HomeGroup.objects.all()

    serializer_class = HomeGroupSerializer
    serializer_read_class = HomeGroupReadSerializer

    permission_classes = (IsAuthenticated,)
    permission_retrieve_classes = (IsAuthenticated, CanSeeHomeGroup)
    permission_create_classes = (IsAuthenticated, CanCreateHomeGroup,)
    permission_update_classes = (IsAuthenticated, CanEditHomeGroup,)
    permission_partial_update_classes = permission_update_classes
    ordering_fields = ()

    def get_permissions(self):
        permission_classes = getattr(self, 'permission_{}_classes'.format(self.action), self.permission_classes)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return self.serializer_read_class
        return self.serializer_class

    def get_queryset(self):
        return self.queryset.for_user(self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if CustomUser.objects.filter(hhome_group_id=instance.id).exists():
            raise exceptions.ValidationError({'message': _('Невозможно удалить Домашнюю Группу. '
                                                           'В составе данной Домашней Группы есть люди.'),
                                              'can_delete': 'false'})

        if instance.meeting_set.exists() and not request.data.get('force'):
            raise exceptions.ValidationError({'message': _('Удаление данной Домашней Группы повлечет за собой. '
                                                           'удаление всех созданных отчетов.'),
                                              'can_delete': 'true'})
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_user(self, request, pk):
        home_group = get_object_or_404(HomeGroup, pk=pk)
        user = self._get_user(request.data.get('user_id', None))
        request.user.can_add_user_to_home_group(user, home_group)

        self._validate_user_for_add_user(user, home_group)
        user.set_home_group_and_log(home_group, get_real_user(request))

        return Response({'detail': 'Пользователь успешно добавлен.'},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def del_user(self, request, pk):
        user_id = request.data.get('user_id', None)
        home_group = get_object_or_404(HomeGroup, pk=pk)
        user = self._get_user(user_id)

        request.user.can_del_user_from_church(user, home_group)
        self._validate_user_for_del_user(user, home_group)

        user.del_home_group_and_log(get_real_user(request))

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'],
            filter_backends=(
                    FilterPotentialHGLeadersByMasterTree,
                    FilterPotentialHGLeadersByChurch,
                    FilterPotentialHGLeadersByDepartment,))
    def potential_leaders(self, request):
        """
        Potential leaders
        """
        leaders = self.filter_queryset(CustomUser.objects.filter(hierarchy__level__gte=1))

        return Response(UserNameSerializer(leaders, many=True).data)

    @action(detail=False, methods=['GET'],
            filter_backends=(FilterHGLeadersByMasterTree, FilterHGLeadersByChurch, FilterHGLeadersByDepartment,))
    def leaders(self, request):
        """
        Leaders
        """
        leaders = self.filter_queryset(CustomUser.objects.filter(home_group__leader__isnull=False)).distinct()

        return Response(UserNameSerializer(leaders, many=True).data)

    @action(detail=True, methods=["GET"])
    def statistics(self, request, pk):
        stats = {}
        home_group = get_object_or_404(HomeGroup, pk=pk)

        stats['users_count'] = home_group.uusers.count()
        stats['fathers_count'] = home_group.uusers.filter(spiritual_level=CustomUser.FATHER).count()
        stats['juniors_count'] = home_group.uusers.filter(spiritual_level=CustomUser.JUNIOR).count()
        stats['babies_count'] = home_group.uusers.filter(spiritual_level=CustomUser.BABY).count()
        stats['partners_count'] = home_group.uusers.filter(partners__is_active=True).count()

        serializer = HomeGroupStatsSerializer
        stats = serializer(stats)
        return Response(stats.data)

    @action(detail=False, methods=['GET'], serializer_class=AllHomeGroupsListSerializer,
            pagination_class=ForSelectPagination)
    def for_select(self, request):
        home_groups = HomeGroup.objects.all()

        department_id = request.query_params.get('department_id')
        if department_id:
            home_groups = home_groups.filter(church__department_id=department_id)

        church_id = request.query_params.get('church_id')
        if church_id:
            home_groups = home_groups.filter(church_id=church_id)

        leader_id = request.query_params.get('leader_id')
        if leader_id:
            home_groups = home_groups.filter(leader_id=leader_id)

        master_tree = request.query_params.get('master_tree')
        if master_tree:
            home_groups = HomeGroup.objects.for_user(CustomUser.objects.get(id=master_tree))

        home_groups = self.serializer_class(home_groups, many=True)
        return Response(home_groups.data)

    @action(detail=True, methods=['POST'])
    def create_report(self, request, pk):
        home_group = self.get_object()
        str_date = request.data.get('date', timezone.now().date().strftime('%Y-%m-%d'))
        meeting_type = get_object_or_404(MeetingType, pk=request.data.get('type_id'))

        date = pytz.utc.localize(datetime.strptime(str_date, '%Y-%m-%d'))
        start_week_day, end_week_date = week_range(date)
        start_week_day = start_week_day.strftime('%Y-%m-%d')
        end_week_date = end_week_date.strftime('%Y-%m-%d')

        if Meeting.objects.filter(home_group=home_group,
                                  type=meeting_type,
                                  date__gte=start_week_day,
                                  date__lte=end_week_date,
                                  ).exists():
            raise exceptions.ValidationError(
                {'message': _('Невозможно создать отчет. '
                              'На данной неделе отчет типа {%s} уже создан.' % meeting_type)})

        Meeting.objects.get_or_create(home_group=home_group,
                                      owner=home_group.leader,
                                      date=date,
                                      type=meeting_type)

        return Response({'message': _('Отчет успешно создан')}, status=status.HTTP_200_OK)

    # Helpers

    @staticmethod
    def _get_master(master, master_tree_id):
        if not master_tree_id:
            return master
        try:
            return master.__class__.get_tree(master).filter(hierarchy__level__gte=1).get(pk=master_tree_id)
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

    @action(detail=False, methods=['GET'])
    def visits_stats(self, request):
        return Response(data={})


class HomeGroupLocationListView(LocationMixin, HomeGroupTableView):
    serializer_class = HomeGroupLocationSerializer


class VoHGListView(GenericAPIView):
    queryset = HomeGroup.objects.all()
    serializer_class = VoHGSerializer
    permission_classes = (VoCanSeeHomeGroup,)
    filter_backends = (VoHomeGroupsDepartmentFilter,)
    pagination_class = None

    def get_queryset(self):
        return super().get_queryset().filter(active=True)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        only_fields = self.request.query_params.getlist('only_fields')

        # ['field1,field2', 'field3'] -> ['field1', 'field2', 'field3']
        only_fields = list(chain(*[f.split(',') for f in only_fields]))
        extra = {
            'only_fields': only_fields
        }
        ctx.update(extra)

        return ctx


class VoDirectionListView(GenericAPIView):
    queryset = Direction.objects.all()
    serializer_class = VoDirectionSerializer
    permission_classes = (VoCanSeeDirection,)
    pagination_class = None

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
