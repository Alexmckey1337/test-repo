# -*- coding: utf-8
from __future__ import unicode_literals

import django_filters
import rest_framework_filters as filters_new
from dbmail import send_db_mail
from django.db.models import Sum, Value as V
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.filters import BaseFilterBackend
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings

from account.models import CustomUser
from common.views_mixins import ExportViewSetMixin
from navigation.table_fields import user_table, summit_table
from payment.views_mixins import CreatePaymentMixin, ListPaymentMixin
from summit.permissions import IsSupervisorOrHigh, IsSupervisorOrConsultantReadOnly
from summit.utils import generate_ticket
from .models import Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson, SummitUserConsultant
from .resources import get_fields, SummitAnketResource
from .serializers import (
    SummitSerializer, SummitTypeSerializer, SummitUnregisterUserSerializer, SummitAnketSerializer,
    SummitAnketNoteSerializer, SummitAnketWithNotesSerializer, SummitLessonSerializer, SummitAnketForSelectSerializer,
    SummitTypeForAppSerializer, SummitAnketForAppSerializer)


def get_success_headers(data):
    try:
        return {'Location': data[api_settings.URL_FIELD_NAME]}
    except (TypeError, KeyError):
        return {}


class SummitPagination(PageNumberPagination):
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
            'common_table': summit_table(),
            'user_table': user_table(self.request.user, prefix_ordering_title='user__'),
            'results': data
        })


class FilterByClub(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Return a filtered queryset.
        """
        params = request.query_params
        summit_id = params.get('summit')
        is_member = params.get('is_member', None)
        if summit_id and is_member in ('true', 'false'):
            is_member = True if is_member == 'true' else False
            summit_type = Summit.objects.get(id=summit_id).type
            users = summit_type.summits.filter(ankets__visited=True).values_list('ankets__user', flat=True)
            if is_member:
                return queryset.filter(user__id__in=set(users))
            return queryset.exclude(user__id__in=set(users))
        return queryset


class SummitAnketTableViewSet(viewsets.ModelViewSet,
                              CreatePaymentMixin,
                              ListPaymentMixin, ExportViewSetMixin):
    queryset = SummitAnket.objects.select_related(
        'user', 'user__hierarchy', 'user__master', 'summit', 'summit__type'). \
        prefetch_related('user__divisions', 'user__departments', 'emails').annotate(
        total_sum=Coalesce(Sum('payments__effective_sum'), V(0))).order_by(
        'user__last_name', 'user__first_name', 'user__middle_name')
    serializer_class = SummitAnketSerializer
    pagination_class = SummitPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       FilterByClub,
                       )
    filter_fields = ('user',
                     'summit', 'visited',
                     'user__master',
                     'user__departments',
                     'user__first_name', 'user__last_name',
                     'user__middle_name', 'user__born_date', 'user__country',
                     'user__region', 'user__city', 'user__district',
                     'user__address', 'user__skype', 'user__phone_number',
                     'user__email', 'user__hierarchy__level', 'user__facebook',
                     'user__vkontakte',
                     )
    search_fields = ('user__first_name',
                     'user__last_name',
                     'user__middle_name',
                     'user__search_name',
                     'user__hierarchy__title',
                     'user__phone_number',
                     'user__city',
                     'user__master__last_name',
                     'user__email',
                     )
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__district',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__facebook',
                       'user__vkontakte',)
    permission_classes = (IsAuthenticated,)

    resource_class = SummitAnketResource

    def get_queryset(self):
        summit_ids = set(self.request.user.summit_ankets.filter(
            role__gte=SummitAnket.CONSULTANT).values_list('summit_id', flat=True))
        return self.queryset.filter(summit__in=summit_ids)

    @list_route(methods=['post'], )
    def post_anket(self, request):
        keys = request.data.keys()
        if not ('user_id' in keys and 'summit_id' in keys):
            return Response({"message": "Некоректные данные", 'status': False})

        user = CustomUser.objects.filter(id=request.data['user_id']).first()
        if not user:
            return Response({"message": "Такого пользователя не существует", 'status': False})

        summit = Summit.objects.filter(id=request.data['summit_id']).first()
        if not summit:
            return Response({"message": "Такой саммит отсутствует", 'status': False})

        anket = SummitAnket.objects.filter(user=user, summit=summit)
        visited = request.data.get('visited', None)
        if anket.exists():
            anket = anket.get()
            if len(request.data['description']) > 0:
                anket.description = request.data['description']
            if visited in (True, False):
                anket.visited = visited
            anket.save()
        else:
            anket = SummitAnket.objects.create(
                user=user, summit=summit, visited=visited, description=request.data['description'])
            if 'retards' in keys:
                if request.data['retards']:
                    anket.retards = request.data['retards']
                    anket.code = request.data['code']
            get_fields(anket)
        data = {"message": "Данные успешно сохраненны",
                'status': True}
        if (data['status'] and request.data.get('send_email', False) and
                anket.summit.mail_template and anket.user.email and
                (int(request.user.id) == 4035 or True)):
            attach = generate_ticket(anket.code)
            pdf_name = '{} ({}).pdf'.format(anket.user.fullname, anket.code)
            send_db_mail(
                anket.summit.mail_template.slug,
                anket.user.email,
                anket,
                attachments=[(pdf_name, attach, 'application/pdf')],
                signals_kwargs={'anket': anket}
            )

        return Response(data)

    @detail_route(methods=['get'])
    def notes(self, request, pk=None):
        serializer = SummitAnketNoteSerializer
        anket = self.get_object()
        queryset = anket.notes

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'])
    def create_note(self, request, pk=None):
        text = request.data['text']
        data = {
            'text': text,
            'summit_anket': pk
        }
        serializer = SummitAnketNoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user.customuser)
        headers = get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SummitLessonViewSet(viewsets.ModelViewSet):
    queryset = SummitLesson.objects.all()
    serializer_class = SummitLessonSerializer

    @detail_route(methods=['post'])
    def add_viewer(self, request, pk=None):
        anket_id = request.data['anket_id']
        lesson = self.get_object()
        anket = get_object_or_404(SummitAnket, pk=anket_id)

        current_user_anket = SummitAnket.objects.filter(
            user=request.user, summit=anket.summit, role__gte=SummitAnket.CONSULTANT)
        is_consultant = SummitUserConsultant.objects.filter(
            consultant=current_user_anket, user_id=anket_id, summit=anket.summit).exists()
        if not is_consultant:
            return Response({'message': 'Только консультант может отмечать уроки.',
                             'lesson_id': pk,
                             'checked': False},
                            status=status.HTTP_400_BAD_REQUEST)

        lesson.viewers.add(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': True})

    @detail_route(methods=['post'])
    def del_viewer(self, request, pk=None):
        anket_id = request.data['anket_id']
        lesson = self.get_object()
        anket = get_object_or_404(SummitAnket, pk=anket_id)

        current_user_anket = SummitAnket.objects.filter(
            user=request.user, summit=anket.summit, role__gte=SummitAnket.CONSULTANT)
        is_consultant = SummitUserConsultant.objects.filter(
            consultant=current_user_anket, user_id=anket_id, summit=anket.summit).exists()
        if not is_consultant:
            return Response({'message': 'Только консультант может отмечать уроки.',
                             'lesson_id': pk,
                             'checked': True},
                            status=status.HTTP_400_BAD_REQUEST)

        lesson.viewers.remove(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': False})


class SummitAnketWithNotesViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.select_related('user', 'user__hierarchy', 'user__master'). \
        prefetch_related('user__divisions', 'user__departments', 'notes')
    serializer_class = SummitAnketWithNotesSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('user',)


class SummitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Summit.objects.prefetch_related('lessons').order_by('-start_date')
    serializer_class = SummitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('type',)
    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['get'])
    def lessons(self, request, pk=None):
        serializer = SummitLessonSerializer
        summit = self.get_object()
        queryset = summit.lessons

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'], )
    def add_lesson(self, request, pk=None):
        name = request.data['name']
        data = dict()
        data['name'] = name
        data['summit'] = pk
        serializer = SummitLessonSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['get'])
    def consultants(self, request, pk=None):
        serializer = SummitAnketForSelectSerializer
        summit = self.get_object()
        queryset = summit.consultants

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'], )
    def add_consultant(self, request, pk=None):
        summit = self.get_object()

        user_perm = IsSupervisorOrHigh().has_object_permission(request, None, summit)
        if not user_perm:
            return Response({'result': 'У вас нет прав для добавления консультантов.'},
                            status=status.HTTP_403_FORBIDDEN)

        anket_id = request.data['anket_id']
        anket = get_object_or_404(SummitAnket, pk=anket_id)
        if anket.summit != summit:
            return Response({'result': 'Выбранная анкета не соответствует данному саммиту.'},
                            status=status.HTTP_400_BAD_REQUEST)
        anket.role = SummitAnket.CONSULTANT
        anket.save()
        data = {'summit_id': int(pk), 'consultant_id': anket_id, 'action': 'added'}

        return Response(data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'], )
    def del_consultant(self, request, pk=None):
        summit = self.get_object()

        user_perm = IsSupervisorOrHigh().has_object_permission(request, None, summit)
        if not user_perm:
            return Response({'result': 'У вас нет прав для удаления консультантов.'},
                            status=status.HTTP_403_FORBIDDEN)

        anket_id = request.data['anket_id']
        anket = get_object_or_404(SummitAnket, pk=anket_id)
        if anket.summit != summit:
            return Response({'result': 'Выбранная анкета не соответствует данному саммиту.'},
                            status=status.HTTP_400_BAD_REQUEST)
        anket.role = SummitAnket.VISITOR
        anket.save()
        data = {'summit_id': int(pk), 'consultant_id': anket_id, 'action': 'removed'}

        return Response(data, status=status.HTTP_204_NO_CONTENT)


class SummitTypeForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitType.objects.prefetch_related('summits')
    serializer_class = SummitTypeForAppSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class ProductFilter(django_filters.FilterSet):
    min_id = django_filters.NumberFilter(name="id", lookup_expr='gte')
    max_id = django_filters.NumberFilter(name="id", lookup_expr='lte')

    class Meta:
        model = SummitAnket
        fields = ['summit', 'min_id', 'max_id']


class SummitAnketForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user').order_by('id')
    serializer_class = SummitAnketForAppSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    # filter_fields = ('summit', 'id')
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ProductFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class SummitTypeViewSet(viewsets.ModelViewSet):
    queryset = SummitType.objects.all()
    serializer_class = SummitTypeSerializer
    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['get'], )
    def is_member(self, request, pk=None):
        user_id = request.query_params.get('user_id')
        if user_id and not user_id.isdigit():
            return Response({'result': 'user_id должен быть числом.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            user_id = request.user.id
        data = {
            'result': SummitAnket.objects.filter(
                user_id=user_id, summit__type_id=pk, visited=True).exists(),
            'user_id': user_id,
        }

        return Response(data)


class SummitUnregisterFilter(filters_new.FilterSet):
    summit_id = filters_new.CharFilter(name="summit_ankets__summit__id", exclude=True)

    class Meta:
        model = CustomUser
        fields = ['summit_id']


class SummitUnregisterUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = SummitUnregisterUserSerializer
    filter_backends = (filters.SearchFilter,
                       filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = SummitUnregisterFilter
    search_fields = ('first_name', 'last_name', 'middle_name',)


class SummitAnketNoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SummitAnketNote.objects.all()
    serializer_class = SummitAnketNoteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('summit_anket',)
    permission_classes = (IsAuthenticated,)


def generate_code(request):
    code = request.GET.get('code', '00000000')

    pdf = generate_ticket(code)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;'

    response.write(pdf)

    return response
