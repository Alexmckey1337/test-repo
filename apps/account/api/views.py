# -*- coding: utf-8
from __future__ import unicode_literals

import json
import logging

import requests
from django.contrib.auth import logout as django_logout
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django_filters import rest_framework
from rest_auth.views import LogoutView as RestAuthLogoutView
from rest_framework import filters
from rest_framework import status, mixins, exceptions
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.account.api.filters import (
    FilterByUserBirthday, UserFilter, ShortUserFilter, FilterMasterTreeWithSelf,
    FilterDashboardMasterTreeWithSelf, UserIsPartnershipFilter, UserChurchFilter,
    UserHomeGroupFilter, UserHGLeadersFilter)
from apps.account.api.pagination import DashboardPagination
from apps.account.api.permissions import (
    CanSeeUserList, CanCreateUser, CanExportUserList, SeeUserListPermission,
    EditUserPermission, ExportUserListPermission, IsSuperUser)
from apps.account.api.serializers import (
    HierarchyError, UserForMoveSerializer, UserUpdateSerializer, ChurchIdSerializer,
    HomeGroupIdSerializer, ManagerIdSerializer)
from apps.account.api.serializers import UserForSelectSerializer
from apps.account.api.serializers import (
    UserShortSerializer, UserTableSerializer, UserSingleSerializer, ExistUserSerializer,
    UserCreateSerializer, DashboardSerializer, DuplicatesAvoidedSerializer,
)
from apps.account.models import CustomUser as User
from apps.account.resources import UserResource
from apps.analytics.decorators import log_perform_update, log_perform_create
from apps.analytics.mixins import LogAndCreateUpdateDestroyMixin
from common.filters import FieldSearchFilter, OrderingFilter
from common.pagination import ForSelectPagination
from common.parsers import MultiPartAndJsonParser
from common.test_helpers.utils import get_real_user
from common.views_mixins import ExportViewSetMixin, ModelWithoutDeleteViewSet
from apps.group.models import HomeGroup, Church
from apps.hierarchy.api.serializers import DepartmentSerializer
from apps.navigation.table_fields import user_table

logger = logging.getLogger(__name__)


def get_reverse_fields(cls, obj):
    rev_fields = dict()
    for field in cls.get_tracking_reverse_fields():
        rev_fields[field] = {
            "value": list(getattr(obj, field).values_list('id', flat=True)),
            'verbose_name': field
        }
    return rev_fields


class UserPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'user_table': user_table(self.request.user),
            'results': data
        })


class DuplicatesAvoidedPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class UserForSelectView(mixins.ListModelMixin, GenericAPIView):
    queryset = User.objects.select_related(
        'hierarchy').order_by('last_name', 'first_name', 'middle_name')

    serializer_class = UserForSelectSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = ForSelectPagination

    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,
                       FilterMasterTreeWithSelf)
    filter_class = ShortUserFilter
    search_fields = ('first_name', 'last_name', 'middle_name')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.annotate(
            full_name=Concat('last_name', V(' '), 'first_name', V(' '), 'middle_name'))

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('without_pagination', None) is not None:
            return None
        return super().paginate_queryset(queryset)


class UserExportViewSetMixin(ExportViewSetMixin):
    @list_route(methods=['post'], permission_classes=(IsAuthenticated, CanExportUserList))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class UserViewSet(LogAndCreateUpdateDestroyMixin, ModelWithoutDeleteViewSet, UserExportViewSetMixin):
    queryset = User.objects.select_related(
        'hierarchy', 'master__hierarchy').prefetch_related(
        'divisions', 'departments'
    ).filter(is_active=True).order_by('last_name', 'first_name', 'middle_name')

    serializer_class = UserUpdateSerializer
    serializer_list_class = UserTableSerializer
    serializer_create_class = UserCreateSerializer
    serializer_update_class = UserUpdateSerializer
    serializer_single_class = UserSingleSerializer

    pagination_class = UserPagination
    filter_backends = (
        rest_framework.DjangoFilterBackend,
        FieldSearchFilter,
        OrderingFilter,
        FilterByUserBirthday,
        FilterMasterTreeWithSelf,
        UserIsPartnershipFilter,
        UserChurchFilter,
        UserHomeGroupFilter,
        UserHGLeadersFilter,
    )
    permission_classes = (IsAuthenticated,)
    permission_list_classes = (IsAuthenticated, CanSeeUserList)
    permission_create_classes = (IsAuthenticated, CanCreateUser)

    ordering_fields = ('first_name', 'last_name', 'middle_name',
                       'born_date', 'country', 'region', 'city', 'disrict', 'address', 'skype',
                       'phone_number', 'email', 'hierarchy__level',
                       'facebook', 'vkontakte', 'master__last_name',)
    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
        'search_email': ('email',),
        'search_phone_number': ('phone_number',),
        'search_country': ('country',),
        'search_city': ('city',),
    }
    filter_class = UserFilter

    parser_classes = (MultiPartAndJsonParser, JSONParser, FormParser)

    parser_list_fields = ['departments', 'divisions', 'extra_phone_numbers']
    parser_dict_fields = ['partner']

    resource_class = UserResource

    def list(self, request, *args, **kwargs):
        """
        Getting list of users for table


        By default ordering by ``last_name``, ``first_name``, ``middle_name``.
        Pagination by 30 users per page. Filtered only active users.
        """
        return super().list(request, *args, **kwargs)

    @detail_route(methods=['post'], serializer_class=HomeGroupIdSerializer)
    def set_home_group(self, request, pk):
        """
        Set home group for user
        """
        user = self.get_object()
        home_group = self._get_object_or_error(HomeGroup, 'home_group_id')
        user.set_home_group_and_log(home_group, get_real_user(request))

        return Response({'detail': 'Домашняя группа установлена.'},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'], serializer_class=ChurchIdSerializer)
    def set_church(self, request, pk):
        """
        Set church for user
        """
        user = self.get_object()
        church = self._get_object_or_error(Church, 'church_id')
        user.set_church_and_log(church, get_real_user(request))

        return Response({'detail': _('Церковь установлена.')},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'],
                  serializer_class=ManagerIdSerializer,
                  permission_classes=(IsSuperUser,))
    def set_manager(self, request, pk):
        """
        Set manager for user
        """
        user = self.get_object()
        manager = self._get_object_or_error(User, 'manager_id')
        user.manager = manager
        user.save()

        return Response({'detail': _('Менеджер назначен.')},
                        status=status.HTTP_200_OK)

    # TODO tmp
    @detail_route(methods=['get'])
    def departments(self, request, pk):
        """
        List of user.departments
        """
        departments = get_object_or_404(User, pk=pk).departments.all()
        serializer = DepartmentSerializer(departments, many=True)

        return Response(serializer.data)

    def _get_object_or_error(self, model, field_name):
        obj_id = self.request.data.get(field_name, None)
        if not obj_id:
            raise exceptions.ValidationError({'detail': _('"%s" is required.' % field_name)})
        try:
            obj = get_object_or_404(model, pk=obj_id)
        except Http404:
            raise exceptions.ValidationError({'detail': _('Object with pk = %s does not exist.' % obj_id)})
        return obj

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'current' and request.user.is_authenticated:
            kwargs['pk'] = request.user.pk
        return super(UserViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'list':
            return [permission() for permission in self.permission_list_classes]
        if self.action == 'create':
            return [permission() for permission in self.permission_create_classes]
        return super(UserViewSet, self).get_permissions()

    def get_queryset(self):
        if self.action in ('update', 'partial_update'):
            return EditUserPermission(self.request.user, queryset=self.queryset).get_queryset().order_by(
                'last_name', 'first_name', 'middle_name')
        elif self.action == 'export':
            return ExportUserListPermission(self.request.user, queryset=self.queryset).get_queryset().order_by(
                'last_name', 'first_name', 'middle_name')
        else:
            return SeeUserListPermission(self.request.user, queryset=self.queryset).get_queryset().order_by(
                'last_name', 'first_name', 'middle_name')

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action == 'retrieve':
            return self.serializer_single_class
        if self.action == 'create':
            return self.serializer_create_class
        if self.action in ('update', 'partial_update'):
            return self.serializer_update_class
        return self.serializer_class

    def get_user_disciples(self, user):
        disciples = user.disciples.all()
        serializer = UserForMoveSerializer(disciples, many=True)
        return serializer.data

    def partial_update(self, request, *args, **kwargs):
        """
        Partial update of the user
        """
        return super().partial_update(request, *args, **kwargs)

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        pass
        # new_obj = kwargs.get('new_obj')
        # self._update_divisions(new_obj)

    @log_perform_create
    def perform_create(self, serializer, **kwargs):
        user = kwargs.get('new_obj')

        return user

    def update(self, request, *args, **kwargs):
        """
        Update of the user
        """
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        try:
            serializer.is_valid(raise_exception=True)
        except HierarchyError:
            data = {
                'detail': _('Please, move disciples before reduce hierarchy.'),
                'disciples': self.get_user_disciples(user),
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                self.perform_update(serializer)
        except IntegrityError as err:
            data = {'detail': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create new user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                user = self.perform_create(serializer)
        except IntegrityError as err:
            data = {'detail': _('При сохранении возникла ошибка. Попробуйте еще раз.')}
            logger.error(err)
            return Response(data, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        serializer = self.serializer_single_class(user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['GET'], serializer_class=DashboardSerializer)
    def dashboard_counts(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = self.request.user

        current_user_descendants = user.__class__.get_tree(user)

        # TODO refactoring
        result = {
            'total_peoples': current_user_descendants.count(),
            'babies_count': current_user_descendants.filter(spiritual_level=User.BABY).count(),
            'juniors_count': current_user_descendants.filter(spiritual_level=User.JUNIOR).count(),
            'fathers_count': current_user_descendants.filter(spiritual_level=User.FATHER).count(),
            'leaders_count': current_user_descendants.filter(home_group__leader__isnull=False).distinct().count()
        }

        result = self.serializer_class(result)
        return Response(result.data)

    @list_route(methods=['GET'], serializer_class=DuplicatesAvoidedSerializer,
                pagination_class=DuplicatesAvoidedPagination)
    def duplicates_avoided(self, request):
        valid_keys = ['last_name', 'first_name', 'middle_name']
        params = [(k, v) for (k, v) in request.query_params.items() if k in valid_keys]

        users = []
        count = 0
        for k, v in params:
            count += 1
            users += User.objects.annotate(similarity=TrigramSimilarity(k, v)).filter(similarity__gt=0.4)

        if request.query_params.get('phone_number'):
            count += 1
            users += User.objects.filter(phone_number__contains=request.query_params.get('phone_number'))

        def get_duplicates(users, count):
            _dict = {}
            for user in users:
                if user not in _dict:
                    _dict[user] = 1
                else:
                    _dict[user] += 1
            return [(x, y) for (x, y) in _dict.items() if y == count]

        users_list = get_duplicates(users, count)
        users = [user[0] for user in users_list]

        if request.query_params.get('only_count'):
            return Response({'count': len(users_list)}, status=status.HTTP_200_OK)

        page = self.paginate_queryset(users)
        if page is not None:
            users = self.get_serializer(page, many=True)
            return self.get_paginated_response(users.data)

        users = self.serializer_class(users, many=True)
        return Response(users.data, status=status.HTTP_200_OK)


class UserShortViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.exclude(hierarchy__level=0).select_related(
        'hierarchy').order_by()
    serializer_class = UserShortSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    filter_backends = (rest_framework.DjangoFilterBackend,
                       filters.SearchFilter,
                       FilterMasterTreeWithSelf,
                       filters.OrderingFilter,)
    # filter_fields = ('first_name', 'last_name', 'hierarchy')
    filter_class = ShortUserFilter
    search_fields = ('first_name', 'last_name', 'middle_name')

    def get_queryset(self):
        exclude_by_user_tree = self.request.query_params.get('exclude_by_user_tree', None)
        if exclude_by_user_tree is not None:
            user = get_object_or_404(User, pk=exclude_by_user_tree)
            descendants = user.get_descendants()
            return self.queryset.exclude(pk__in=descendants.values_list('pk', flat=True))
        return self.queryset

    def filter_queryset(self, queryset):
        include_user = self.request.query_params.get('include_user')
        if include_user:
            return super().filter_queryset(queryset).union(self.queryset.filter(pk=include_user))
        return super().filter_queryset(queryset)


class DashboardMasterTreeFilterViewSet(ModelWithoutDeleteViewSet):
    queryset = User.objects.exclude(hierarchy__level=0).exclude(is_active=False).select_related(
        'hierarchy').order_by('last_name')
    serializer_class = UserShortSerializer
    pagination_class = DashboardPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (FilterDashboardMasterTreeWithSelf,
                       filters.SearchFilter,)

    filter_class = ShortUserFilter
    search_fields = ('first_name', 'last_name', 'middle_name')


class ExistUserListViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.exclude(hierarchy__level=0).select_related(
        'hierarchy').order_by()
    serializer_class = ExistUserSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    filter_backends = (FieldSearchFilter,)
    field_search_fields = {
        'search_last_name': ('last_name',),
        'search_email': ('email',),
        'search_phone_number': ('phone_number',),
    }

    def list(self, request, *args, **kwargs):
        params = self.field_search_fields.keys()
        for f in params:
            param = request.query_params.get(f, '')
            if param and len(param) < 5:
                return Response({'detail': _('Min length of %s == 4' % f)},
                                status=status.HTTP_400_BAD_REQUEST)
        if not len(['go' for p in params if len(request.query_params.get(p, '')) > 0]):
            return Response(
                {'detail': _('One of [%s] parameters is required' % ', '.join(params))},
                status=status.HTTP_400_BAD_REQUEST)
        return super(ExistUserListViewSet, self).list(request, *args, **kwargs)


class LogoutView(RestAuthLogoutView):
    def logout(self, request):
        try:
            key = request._request.COOKIES.get('key', '')
            request.user.auth_tokens.filter(key=key).delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        django_logout(request)

        return Response({"success": _("Successfully logged out.")},
                        status=status.HTTP_200_OK)