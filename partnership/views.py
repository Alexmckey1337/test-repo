# -*- coding: utf-8
from __future__ import unicode_literals

from datetime import datetime

import django_filters
from django.db.models import Case, IntegerField
from django.db.models import Sum
from django.db.models import Value
from django.db.models import When
from django.db.models.functions import Concat
from django.utils import six
from rest_framework import filters
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import CustomUser as User, CustomUser
from navigation.models import user_table, user_partner_table
from partnership.permissions import IsManagerOrHigh, IsSupervisorOrHigh, IsSupervisorOrManagerReadOnly
from .models import Partnership, Deal
from .serializers import PartnershipSerializer, DealSerializer, NewPartnershipSerializer, \
    PartnershipUnregisterUserSerializer, PartnershipForEditSerializer


class SaganPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 2


class PartnershipPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'common_table': user_partner_table(self.request.user),
            'user_table': user_table(self.request.user),
            'results': data
        })


class PartnershipViewSet(viewsets.ModelViewSet):
    queryset = Partnership.objects.all()
    serializer_class = PartnershipSerializer
    pagination_class = PartnershipPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible__user',)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name', 'user__search_name',
                     'user__country', 'user__region', 'user__city', 'user__district',
                     'user__address', 'user__skype', 'user__phone_number', 'user__hierarchy__title',
                     'user__department__title',
                     'user__email',)
    ordering_fields = ('user__first_name', 'user__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__department__title', 'user__facebook',
                       'user__vkontakte',)
    permission_classes = (IsManagerOrHigh,)

    def get_queryset(self):
        user = self.request.user
        user_perm = IsSupervisorOrHigh()
        if not Partnership.objects.filter(user=user).exists():
            return self.queryset.none()
        if user_perm.has_permission(self.request, None):
            return self.queryset
        return self.queryset.select_related('responsible__user').filter(responsible__user=user)


class NewPartnershipViewSet(mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = Partnership.objects \
        .select_related('user', 'user__hierarchy', 'user__department', 'user__master', 'responsible__user') \
        .prefetch_related('user__divisions') \
        .order_by('user__last_name', 'user__first_name', 'user__middle_name')
    serializer_class = NewPartnershipSerializer
    pagination_class = PartnershipPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible__user', 'responsible')
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name', 'user__search_name',
                     'user__country', 'user__region', 'user__city', 'user__district',
                     'user__address', 'user__skype', 'user__phone_number', 'user__hierarchy__title',
                     'user__department__title',
                     'user__email',)
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__department__title', 'user__facebook',
                       'user__vkontakte', 'value', 'responsible__user__last_name')
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        user_perm = IsSupervisorOrHigh()
        if not Partnership.objects.filter(user=user).exists():
            return self.queryset.none()
        if user_perm.has_permission(self.request, None):
            return self.queryset
        return self.queryset.select_related('responsible__user').filter(responsible__user=user)

    @list_route()
    def simple(self, request):
        partnerships = Partnership.objects.select_related('user').filter(
            level__lte=Partnership.MANAGER).values_list(
            'id', 'user__last_name', 'user__first_name', 'user__middle_name')
        partnerships = [{'id': p[0], 'fullname': '{} {} {}'.format(*p[1:])} for p in partnerships]
        return Response(partnerships)

    @list_route()
    def for_edit(self, request):
        user_id = request.query_params.get('user')
        user = get_object_or_404(CustomUser, pk=user_id)
        partnership = get_object_or_404(Partnership, user=user)

        data = PartnershipForEditSerializer(partnership).data
        return Response(data)

    @detail_route(methods=['put'])
    def update_need(self, request, pk=None):
        text = request.data['need_text']
        parntership = get_object_or_404(Partnership, pk=pk)
        parntership.need_text = text
        parntership.save()

        return Response({'need_text': text})

    @list_route(methods=['get'])
    def stats(self, request):
        request_partner_id = request.query_params.get('partner_id')

        current_user = request.user
        current_partner = get_object_or_404(Partnership, user=current_user)

        if current_partner.level > Partnership.MANAGER:
            return Response({'detail': 'Статистику можно просматривать только менеджерам.'},
                            status=status.HTTP_403_FORBIDDEN)
        elif current_partner.level == Partnership.MANAGER or not request_partner_id:
            partnership = current_partner
        else:
            partnership = get_object_or_404(Partnership, id=request_partner_id)

        partners = self._get_partners_list(partnership)

        stat = self._get_partners_stats(partners)

        return Response(stat)

    @staticmethod
    def _get_partners_stats(partners):
        stat_keys = ('total_deals', 'paid_deals', 'unpaid_deals',
                     'sum_deals', 'value',
                     'paid_sum_deals', 'unpaid_sum_deals')
        stat = {}
        for k in stat_keys:
            if k == 'value':
                stat['planned_sum_deals'] = sum([p[k] for p in partners])
            else:
                stat[k] = sum([p[k] for p in partners])

        stat['count_partners'] = len(partners)
        stat['paid_partners'] = len([1 for i in partners if i['is_paid']])
        stat['partial_paid_partners'] = len(
            list(filter(lambda x: x > 0, [p['paid_deals'] for p in partners if not p['is_paid']])))
        stat['unpaid_partners'] = len(partners) - stat['paid_partners'] - stat['partial_paid_partners']

        stat['partners'] = [p for p in partners if p['total_deals'] > 0]

        return stat

    def _get_partners_list(self, partnership):

        month = self.request.query_params.get('month', datetime.now().month)
        year = self.request.query_params.get('year', datetime.now().year)
        partners = list(partnership.disciples.annotate(
            total_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          then=1), default=0,
                     output_field=IntegerField())
            ),
            paid_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=True, then=1), default=0,
                     output_field=IntegerField())
            ),
            unpaid_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=False, then=1), default=0,
                     output_field=IntegerField())
            ),
            sum_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          then='deals__value'), default=0,
                     output_field=IntegerField())
            ),
            paid_sum_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=True, then='deals__value'), default=0,
                     output_field=IntegerField())
            ),
            unpaid_sum_deals=Sum(
                Case(When(deals__date_created__month=month, deals__date_created__year=year,
                          deals__done=False, then='deals__value'), default=0,
                     output_field=IntegerField())
            ),
            partner_name=Concat('user__last_name', Value(' '), 'user__first_name', Value(' '), 'user__middle_name')
        ).values('partner_name',
                 'total_deals', 'paid_deals', 'unpaid_deals',
                 'sum_deals', 'value',
                 'paid_sum_deals', 'unpaid_sum_deals'))

        for p in partners:
            p['is_paid'] = bool(p['paid_sum_deals']) and p['paid_sum_deals'] >= p['value']

        return partners


class DateFilter(filters.FilterSet):
    to_date = django_filters.DateFilter(name="date", lookup_type='lte')
    from_date = django_filters.DateFilter(name="date", lookup_type='gte')

    class Meta:
        model = Deal
        fields = ['partnership__responsible__user',
                  'partnership__user', 'value', 'date',
                  'expired', 'done', 'to_date', 'from_date', ]


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.select_related('partnership')
    serializer_class = DealSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_class = DateFilter
    search_fields = ('partnership__user__first_name',
                     'partnership__user__last_name',
                     'partnership__user__search_name',
                     'partnership__user__middle_name',)
    # pagination_class = SaganPagination
    permission_classes = (IsSupervisorOrManagerReadOnly,)

    def get_queryset(self):
        user = self.request.user
        if Partnership.objects.get(user=user).level < Partnership.MANAGER:
            return self.queryset
        return Deal.objects.select_related(
            'partnership', 'partnership__responsible__user') \
            .filter(partnership__responsible__user=user)

    def perform_update(self, serializer):
        serializer.save()

        partnership = serializer.instance.partnership
        plan_value = partnership.value
        month = datetime.now().month
        complete_value = partnership.deals.filter(
            date_created__month=month).aggregate(values_sum=Sum('value'))['values_sum']
        diff_value = plan_value - complete_value if complete_value else plan_value
        if diff_value > 0:
            Deal.objects.create(value=diff_value, partnership=partnership)


@api_view(['POST'])
def create_partnership(request):
    '''POST: (user, responsible, value)'''

    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user_id = data['user']
        responsible_partnership_id = None
        if 'responsible' in data.keys():
            responsible_partnership_id = data['responsible']
        value = data['value']
        date = data['date']
        try:
            object = Partnership.objects.get(user__id=user_id)
            response_dict['message'] = "Этот пользователь уже имеет партнерство."
            response_dict['status'] = False
        except Partnership.DoesNotExist:
            try:
                user = User.objects.get(id=user_id)
                responsible_partnership = Partnership.objects.filter(id=responsible_partnership_id).first()
                object = Partnership.objects.create(user=user, responsible=responsible_partnership, value=value,
                                                    date=date)
                if object:
                    serializer = PartnershipSerializer(object, context={'request': request})
                    response_dict['data'] = serializer.data
                    response_dict['message'] = "Партнерство успешно добавлено."
                    response_dict['status'] = True
            except User.DoesNotExist:
                response_dict['data'] = []
                response_dict['message'] = "Пользователя не существует."
                response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def update_partnership(request):
    '''POST: (id, responsible, value, date, is_responsible)'''
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        try:
            object = Partnership.objects.get(id=data['id'])
            for key, value in six.iteritems(data):
                if key == "responsible":
                    responsible_partnerhip = Partnership.objects.filter(user__id=value).first()
                    object.responsible = responsible_partnerhip
                else:
                    setattr(object, key, value)
            object.save()
            serializer = PartnershipSerializer(object, context={'request': request})
            response_dict['data'] = serializer.data
            response_dict['message'] = "Партнерство успешно изменено."
            response_dict['status'] = True
        except Partnership.DoesNotExist:
            response_dict['message'] = "Партнерство не существует."
            response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def delete_partnership(request):
    '''POST: (id)'''
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        user_id = data['id']
        try:
            object = Partnership.objects.get(user__id=user_id)
            object.delete()
            response_dict['message'] = "Партнерство успешно удалено."
            response_dict['status'] = True
        except Partnership.DoesNotExist:
            response_dict['message'] = "Такого пользователя не существует."
            response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def change_responsible(request):
    '''POST: (responsible_id, new_responsible_id)'''
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        try:
            responsible = Partnership.objects.get(id=data['responsible_id'])
            disciples = Partnership.objects.filter(responsible=responsible).all()
            try:
                new_responsible = Partnership.objects.get(id=data['responsible_id'])
                disciples.update(responsible=new_responsible)
                response_dict['message'] = "Ответственный был успешно изменен."
                response_dict['status'] = True
            except Partnership.DoesNotExist:
                response_dict['message'] = "Такого ответственного не существует."
                response_dict['status'] = False
        except Partnership.DoesNotExist:
            response_dict['message'] = "Такого ответственного не существует."
            response_dict['status'] = False
    return Response(response_dict)


class PartnershipsUnregisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(partnership__isnull=True)
    serializer_class = PartnershipUnregisterUserSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.DjangoFilterBackend,)
    filter_fields = ('partnership',)
    search_fields = ('first_name', 'last_name', 'middle_name',
                     # 'country', 'region', 'city', 'district',
                     # 'address', 'email',
                     )
    permission_classes = (IsAuthenticated,)
