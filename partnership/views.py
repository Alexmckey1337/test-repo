# -*- coding: utf-8
from models import Partnership, Deal
from serializers import PartnershipSerializer, DealSerializer
from rest_framework.decorators import api_view
from rest_framework import viewsets, filters
from rest_framework.response import Response
from account.models import CustomUser as User
from django.utils.dateparse import parse_date
from rest_framework import filters
from rest_framework import generics
import django_filters
from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from navigation.models import partner_table
import rest_framework_filters as filters_new
from summit.serializers import SummitUnregisterUserSerializer
from rest_framework.permissions import IsAuthenticated

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
            'common_table': partner_table(),
            'results': data
        })


class PartnershipViewSet(viewsets.ModelViewSet):
    queryset = Partnership.objects.all()
    serializer_class = PartnershipSerializer
    pagination_class = PartnershipPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_fields = ('user', 'responsible__user', 'is_responsible',)
    search_fields = ('user__first_name', 'user__last_name', 'user__middle_name',
                     'user__country', 'user__region', 'user__city', 'user__district',
                     'user__address', 'user__skype', 'user__phone_number', 'user__hierarchy__title', 'user__department__title',
                     'user__email', )
    ordering_fields = ('user__first_name', 'user__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__department__title', 'user__facebook',
                       'user__vkontakte',)
    permission_classes = (IsAuthenticated,)


class DateFilter(filters.FilterSet):
    to_date = django_filters.DateFilter(name="date", lookup_type='lte')
    from_date = django_filters.DateFilter(name="date", lookup_type='gte')

    class Meta:
        model = Deal
        fields = ['partnership__responsible__user',
                  'partnership__user', 'value', 'date',
                  'expired', 'done', 'to_date', 'from_date', ]


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,)
    filter_class = DateFilter
    search_fields = ('partnership', )
    #pagination_class = SaganPagination
    permission_classes = (IsAuthenticated,)

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
            response_dict['message'] = u"Этот пользователь уже имеет партнерство."
            response_dict['status'] = False
        except Partnership.DoesNotExist:
            try:
                user = User.objects.get(id=user_id)
                responsible_partnership = Partnership.objects.filter(id=responsible_partnership_id).first()
                object = Partnership.objects.create(user=user, responsible=responsible_partnership, value=value, date=date)
                if object:
                    serializer = PartnershipSerializer(object, context={'request': request})
                    response_dict['data'] = serializer.data
                    response_dict['message'] = u"Партнерство успешно добавлено."
                    response_dict['status'] = True
            except User.DoesNotExist:
                response_dict['data'] = []
                response_dict['message'] = u"Пользователя не существует."
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
            for key, value in data.iteritems():
                if key == "responsible":
                    responsible_partnerhip = Partnership.objects.filter(user__id=value).first()
                    object.responsible = responsible_partnerhip
                else:
                    setattr(object, key, value)
            object.save()
            serializer = PartnershipSerializer(object, context={'request': request})
            response_dict['data'] = serializer.data
            response_dict['message'] = u"Партнерство успешно изменено."
            response_dict['status'] = True
        except Partnership.DoesNotExist:
            response_dict['message'] = u"Партнерство не существует."
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
            response_dict['message'] = u"Партнерство успешно удалено."
            response_dict['status'] = True
        except Partnership.DoesNotExist:
            response_dict['message'] = u"Такого пользователя не существует."
            response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def create_deal(request):
    '''POST: (date user description)'''
    response_dict = dict()

    if request.method == 'POST':
        data = request.data
        date_str = data['date']
        done = data['done']
        date = parse_date(date_str)
        partnership = Partnership.objects.get(user__id=data['user'])
        try:
            object = Deal.objects.get(date__month=date.month, date__year=date.year, partnership=partnership)
            response_dict['message'] = u"Этот пользователь уже имеет сделку за этот месяц."
            response_dict['status'] = False
        except Deal.DoesNotExist:
            object = Deal.objects.create(date=data['date'],
                                         value=partnership.value,
                                         partnership=partnership,
                                         description=data['description'],
                                         done=done)
            if object:
                serializer = DealSerializer(object, context={'request': request})
                response_dict['data'] = serializer.data
                response_dict['message'] = u"Сделка успешно добавлена."
                response_dict['status'] = True
    return Response(response_dict)


@api_view(['POST'])
def update_deal(request):
    '''POST: (id, date value description)'''
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        try:
            object = Deal.objects.get(id=data['id'])
            for key, value in data.iteritems():
                setattr(object, key, value)
            if object.done:
                object.expired = False
            object.save()

            serializer = DealSerializer(object, context={'request': request})
            response_dict['data'] = serializer.data
            response_dict['message'] = u"Сделка успешно изменена."
            response_dict['status'] = True
        except Deal.DoesNotExist:
            response_dict['message'] = u"Сделки не существует."
            response_dict['status'] = False
    return Response(response_dict)


@api_view(['POST'])
def delete_deal(request):
    '''POST: (id)'''
    response_dict = dict()
    if request.method == 'POST':
        data = request.data
        try:
            object = Deal.objects.get(id=data['id'])
            object.delete()
            response_dict['message'] = u"Сделка успешно удалена."
            response_dict['status'] = True
        except Deal.DoesNotExist:
            response_dict['message'] = u"Такой сделки не существует."
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
                response_dict['message'] = u"Ответственный был успешно изменен."
                response_dict['status'] = True
            except Partnership.DoesNotExist:
                response_dict['message'] = u"Такого ответственного не существует."
                response_dict['status'] = False
        except Partnership.DoesNotExist:
            response_dict['message'] = u"Такого ответственного не существует."
            response_dict['status'] = False
    return Response(response_dict)


class PartnershipsUnregisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(partnership=None)
    serializer_class = SummitUnregisterUserSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.DjangoFilterBackend,)
    filter_fields = ('partnership',)
    search_fields = ('first_name', 'last_name', 'middle_name',
                     'country', 'region', 'city', 'district',
                     'address', 'email', )
    permission_classes = (IsAuthenticated,)

