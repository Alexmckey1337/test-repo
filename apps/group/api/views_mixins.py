from django.db.models import Count, Q
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.account.models import CustomUser
from apps.group.api.filters import ChurchAllUserFilter
from apps.group.api.pagination import HomeGroupPagination, GroupUsersPagination
from apps.group.api.serializers import HomeGroupListSerializer, GroupUserSerializer
from apps.group.resources import GroupUserResource, HomeGroupResource
from common.views_mixins import BaseExportViewSetMixin

GROUP_USER_ORDERING_FIELDS = ('id', 'last_name', 'spiritual_level', 'leader__last_name',
                              'phone_number', 'born_date', 'repentance_date')

HOME_GROUP_ORDERING_FIELDS = ('id', 'title', 'city', 'leader__last_name', 'address',
                              'opening_date', 'phone_number', 'website')


class HomeGroupListMixin:
    home_group_serializer_class = HomeGroupListSerializer

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    def filter_queryset(self, qs):  # pragma: no cover
        raise NotImplementedError()

    def paginate_queryset(self, qs):  # pragma: no cover
        raise NotImplementedError()

    def get_paginated_response(self, data):  # pragma: no cover
        raise NotImplementedError()

    @action(detail=True, methods=['get'],
            pagination_class=HomeGroupPagination,
            ordering_fields=HOME_GROUP_ORDERING_FIELDS,
            filter_backends=(filters.OrderingFilter,))
    def home_groups(self, request, pk):
        instance = self.get_object()
        queryset = instance.home_group.annotate(count_users=Count('uusers'))
        queryset = self.filter_queryset(queryset)

        search = request.query_params.get('search', '').strip()
        if search and len(search) >= 3:
            search_queries = map(lambda s: s.strip(), search.split(' '))
            for s in search_queries:
                queryset = queryset.filter(
                    Q(title__istartswith=s) | Q(leader__first_name__istartswith=s) |
                    Q(leader__last_name__istartswith=s))

        page = self.paginate_queryset(queryset)
        users = self.home_group_serializer_class(page, many=True)
        return self.get_paginated_response(users.data)


class BaseUserListMixin:
    user_serializer_class = GroupUserSerializer

    user_field = 'uusers'

    @staticmethod
    def detail_view_users_search(queryset, search):
        search_queries = map(lambda s: s.strip(), search.split(' '))
        for s in search_queries:
            queryset = queryset.filter(
                Q(first_name__istartswith=s) | Q(last_name__istartswith=s) |
                Q(middle_name__istartswith=s) | Q(search_name__icontains=s))

        return queryset

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    def filter_queryset(self, qs):  # pragma: no cover
        raise NotImplementedError()

    def paginate_queryset(self, qs):  # pragma: no cover
        raise NotImplementedError()

    def get_paginated_response(self, data):  # pragma: no cover
        raise NotImplementedError()


class UserListMixin(BaseUserListMixin):
    @action(detail=True, methods=['get'],
            pagination_class=GroupUsersPagination,
            ordering_fields=GROUP_USER_ORDERING_FIELDS,
            filter_backends=(filters.OrderingFilter,))
    def users(self, request, pk):
        instance = self.get_object()
        queryset = getattr(instance, self.user_field).order_by('last_name', 'first_name', 'middle_name')
        queryset = self.filter_queryset(queryset)

        search = request.query_params.get('search', '').strip()
        if search and len(search) >= 3:
            queryset = self.detail_view_users_search(queryset, search)

        page = self.paginate_queryset(queryset)
        users = self.user_serializer_class(page, many=True)
        return self.get_paginated_response(users.data)


class AllUserListMixin(BaseUserListMixin):
    @action(detail=True, methods=['get'], pagination_class=GroupUsersPagination,
            ordering_fields=GROUP_USER_ORDERING_FIELDS,
            filter_backends=(ChurchAllUserFilter, filters.OrderingFilter,))
    def all_users(self, request, pk):
        queryset = CustomUser.objects.order_by('last_name', 'first_name', 'middle_name')
        queryset = self.filter_queryset(queryset)

        search = request.query_params.get('search', '').strip()
        if search and len(search) >= 3:
            queryset = self.detail_view_users_search(queryset, search)

        page = self.paginate_queryset(queryset)
        users = self.user_serializer_class(page, many=True)
        return self.get_paginated_response(users.data)


class GroupUserExportViewSetMixin(BaseExportViewSetMixin):
    user_field = 'uusers'

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @action(detail=True, methods=['post'], filter_backends=())
    def export_users(self, request, *args, **kwargs):
        fields = self.get_export_fields(request.data)

        instance = self.get_object()
        queryset = getattr(instance, self.user_field).all()
        queryset = self.filter_queryset(queryset)

        return self.get_response(queryset, fields, GroupUserResource)


class ChurchAllUserExportViewSetMixin(BaseExportViewSetMixin):
    user_field = 'uusers'

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @action(detail=True, methods=['post'], filter_backends=(ChurchAllUserFilter,))
    def export_all_users(self, request, *args, **kwargs):
        fields = self.get_export_fields(request.data)

        queryset = CustomUser.objects.all()
        queryset = self.filter_queryset(queryset)

        return self.get_response(queryset, fields, GroupUserResource)


class ChurchHomeGroupExportViewSetMixin(BaseExportViewSetMixin):

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @action(detail=True, methods=['post'], filter_backends=())
    def export_groups(self, request, *args, **kwargs):
        fields = self.get_export_fields(request.data)

        instance = self.get_object()
        queryset = instance.home_group.all()
        queryset = self.filter_queryset(queryset)

        return self.get_response(queryset, fields, HomeGroupResource)


class ChurchUsersMixin(UserListMixin, AllUserListMixin, GroupUserExportViewSetMixin,
                       ChurchAllUserExportViewSetMixin):
    pass


class ChurchHomeGroupMixin(HomeGroupListMixin, ChurchHomeGroupExportViewSetMixin):
    pass


class HomeGroupUsersMixin(UserListMixin, GroupUserExportViewSetMixin):
    pass


class LocationMixin(GenericAPIView):
    ordering_fields = []

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        return super().get_queryset().has_location().order_by()
