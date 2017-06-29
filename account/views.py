# -*- coding: utf-8
from __future__ import unicode_literals

import logging

from django.contrib.auth import logout as django_logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, IntegrityError
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_auth.views import LogoutView as RestAuthLogoutView
from rest_framework import status, mixins, exceptions
from rest_framework import viewsets, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from account.filters import FilterByUserBirthday, UserFilter, ShortUserFilter, FilterMasterTreeWithSelf
from account.models import CustomUser as User
from account.permissions import CanSeeUserList, CanCreateUser, CanExportUserList
from account.serializers import HierarchyError, UserForMoveSerializer
from analytics.decorators import log_perform_update, log_perform_create
from analytics.mixins import LogAndCreateUpdateDestroyMixin
from common.filters import FieldSearchFilter
from common.parsers import MultiPartAndJsonParser
from common.views_mixins import ExportViewSetMixin
from group.models import HomeGroup, Church
from hierarchy.serializers import DepartmentSerializer
from navigation.table_fields import user_table
from .resources import UserResource
from .serializers import UserShortSerializer, UserTableSerializer, UserSerializer, \
    UserSingleSerializer, PartnershipSerializer, ExistUserSerializer, UserCreateSerializer, DashboardSerializer

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


class UserExportViewSetMixin(ExportViewSetMixin):
    @list_route(methods=['post'], permission_classes=(IsAuthenticated, CanExportUserList))
    def export(self, request, *args, **kwargs):
        return self._export(request, *args, **kwargs)


class UserViewSet(LogAndCreateUpdateDestroyMixin, viewsets.ModelViewSet, UserExportViewSetMixin):
    queryset = User.objects.select_related(
        'hierarchy', 'master__hierarchy').prefetch_related(
        'divisions', 'departments'
    ).filter(is_active=True).order_by('last_name', 'first_name', 'middle_name')

    serializer_class = UserSerializer
    serializer_list_class = UserTableSerializer
    serializer_create_class = UserCreateSerializer
    serializer_single_class = UserSingleSerializer

    pagination_class = UserPagination
    filter_backends = (
        filters.DjangoFilterBackend,
        FieldSearchFilter,
        filters.OrderingFilter,
        FilterByUserBirthday,
        FilterMasterTreeWithSelf,
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

    @detail_route(methods=['post'])
    def set_home_group(self, request, pk):
        user = self.get_object()
        home_group = self._get_object_or_error(HomeGroup, 'home_group_id')
        user.set_home_group_and_log(home_group, getattr(request, 'real_user', getattr(request, 'user', None)))

        return Response({'detail': 'Домашняя группа установлена.'},
                        status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def set_church(self, request, pk):
        user = self.get_object()
        church = self._get_object_or_error(Church, 'church_id')
        user.set_church_and_log(church, getattr(request, 'real_user', getattr(request, 'user', None)))

        return Response({'detail': _('Церковь установлена.')},
                        status=status.HTTP_200_OK)

    # TODO tmp
    @detail_route(methods=['get'])
    def departments(self, request, pk):
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
        if kwargs.get('pk') == 'current' and request.user.is_authenticated():
            kwargs['pk'] = request.user.pk
        return super(UserViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'list':
            return [permission() for permission in self.permission_list_classes]
        if self.action == 'create':
            return [permission() for permission in self.permission_create_classes]
        return super(UserViewSet, self).get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset
        if not user.hierarchy:
            return self.queryset.none()
        if self.action in ('list', 'retrieve'):
            return user.get_descendants(include_self=True).select_related(
                'hierarchy', 'master__hierarchy').prefetch_related(
                'divisions', 'departments'
            ).filter(is_active=True).order_by('last_name', 'first_name', 'middle_name')
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        if self.action == 'retrieve':
            return self.serializer_single_class
        if self.action == 'create':
            return self.serializer_create_class
        return self.serializer_class

    def get_user_disciples(self, user):
        disciples = user.disciples.all()
        serializer = UserForMoveSerializer(disciples, many=True)
        return serializer.data

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = self.get_object()
        data = request.data
        serializer = self.get_serializer(user, data=data, partial=partial)
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

    @log_perform_update
    def perform_update(self, serializer, **kwargs):
        new_obj = kwargs.get('new_obj')
        self._update_partnership(new_obj)
        self._update_divisions(new_obj)

    @log_perform_create
    def perform_create(self, serializer, **kwargs):
        user = kwargs.get('new_obj')
        self._create_partnership(user)

        return user

    def create(self, request, *args, **kwargs):
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

    def _create_partnership(self, user):
        partner = self.request.data.get('partner', None)
        if partner is not None and isinstance(partner, dict):
            partner['user'] = user
            serializer = PartnershipSerializer(data=partner)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def _update_divisions(self, user):
        divisions = self.request.data.get('divisions', None)
        if divisions is not None and isinstance(divisions, (list, tuple)):
            user.divisions.set(divisions)

    def _update_partnership(self, user):
        if not hasattr(user, 'partnership'):
            self._create_partnership(user)
            return

        partner = self.request.data.get('partner', None)
        if partner is not None and isinstance(partner, dict):
            partner['user'] = user
            partner_obj = user.partnership
            serializer = PartnershipSerializer(partner_obj, data=partner)
            serializer.is_valid(raise_exception=True)
            serializer.save()

    @list_route(methods=['GET'], serializer_class=DashboardSerializer)
    def dashboard_counts(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = self.request.user

        current_user_descendants = User.objects.get(user_ptr=user).get_descendants()

        # TODO refactoring
        result = {
            'total_peoples': current_user_descendants.count(),
            'babies_count': current_user_descendants.filter(spiritual_level=User.BABY).count(),
            'juniors_count': current_user_descendants.filter(spiritual_level=User.JUNIOR).count(),
            'fathers_count': current_user_descendants.filter(spiritual_level=User.FATHER).count(),
            'leaders_count': current_user_descendants.filter(home_group__leader__isnull=False).count()
        }

        result = self.serializer_class(result)
        return Response(result.data)


class UserShortViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.exclude(hierarchy__level=0).select_related(
        'hierarchy').order_by()
    serializer_class = UserShortSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,
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
