from django.db.models import Count
from rest_framework import filters
from rest_framework.decorators import detail_route

from account.models import CustomUser
from common.views_mixins import BaseExportViewSetMixin
from group.filters import ChurchAllUserFilter
from group.pagination import HomeGroupPagination, GroupUsersPagination
from group.resources import GroupUserResource, HomeGroupResource
from group.serializers import HomeGroupListSerializer, GroupUserSerializer

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

    @detail_route(methods=['get'],
                  pagination_class=HomeGroupPagination,
                  ordering_fields=HOME_GROUP_ORDERING_FIELDS,
                  filter_backends=(filters.OrderingFilter,))
    def home_groups(self, request, pk):
        instance = self.get_object()
        queryset = instance.home_group.annotate(count_users=Count('uusers'))
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        users = self.home_group_serializer_class(page, many=True)
        return self.get_paginated_response(users.data)


class BaseUserListMixin:
    user_serializer_class = GroupUserSerializer

    user_field = 'uusers'

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    def filter_queryset(self, qs):  # pragma: no cover
        raise NotImplementedError()

    def paginate_queryset(self, qs):  # pragma: no cover
        raise NotImplementedError()

    def get_paginated_response(self, data):  # pragma: no cover
        raise NotImplementedError()


class UserListMixin(BaseUserListMixin):
    @detail_route(methods=['get'],
                  pagination_class=GroupUsersPagination,
                  ordering_fields=GROUP_USER_ORDERING_FIELDS,
                  filter_backends=(filters.OrderingFilter,))
    def users(self, request, pk):
        instance = self.get_object()
        queryset = getattr(instance, self.user_field).all()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        users = self.user_serializer_class(page, many=True)
        return self.get_paginated_response(users.data)


class AllUserListMixin(BaseUserListMixin):
    @detail_route(methods=['get'], pagination_class=GroupUsersPagination,
                  ordering_fields=GROUP_USER_ORDERING_FIELDS,
                  filter_backends=(ChurchAllUserFilter, filters.OrderingFilter,))
    def all_users(self, request, pk):
        queryset = CustomUser.objects.all()
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        users = self.user_serializer_class(page, many=True)
        return self.get_paginated_response(users.data)


class GroupUserExportViewSetMixin(BaseExportViewSetMixin):
    user_field = 'uusers'

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @detail_route(methods=['post'], filter_backends=())
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

    @detail_route(methods=['post'], filter_backends=(ChurchAllUserFilter,))
    def export_all_users(self, request, *args, **kwargs):
        fields = self.get_export_fields(request.data)

        queryset = CustomUser.objects.all()
        queryset = self.filter_queryset(queryset)

        return self.get_response(queryset, fields, GroupUserResource)


class ChurchHomeGroupExportViewSetMixin(BaseExportViewSetMixin):

    def get_object(self):  # pragma: no cover
        raise NotImplementedError()

    @detail_route(methods=['post'], filter_backends=())
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
