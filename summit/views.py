# -*- coding: utf-8
from __future__ import unicode_literals

import rest_framework_filters as filters_new
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
from account.serializers import UserShortSerializer
from navigation.models import user_table, user_summit_table
from summit.utils import generate_ticket
from .models import Summit, SummitAnket, SummitType, SummitAnketNote, SummitLesson
from .resources import get_fields
from .serializers import (
    SummitSerializer, SummitTypeSerializer, SummitUnregisterUserSerializer, SummitAnketSerializer,
    SummitAnketNoteSerializer, SummitAnketWithNotesSerializer, SummitLessonSerializer, SummitTypeForAppSerializer,
    SummitAnketForAppSerializer)
from .tasks import send_ticket


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
            'common_table': user_summit_table(),
            'user_table': user_table(self.request.user),
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


class SummitAnketTableViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.select_related('user', 'user__hierarchy', 'user__department', 'user__master'). \
        prefetch_related('user__divisions').order_by('user__last_name', 'user__first_name', 'user__middle_name')
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
                     'user__department__title',
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
                     'user__hierarchy__title',
                     'user__phone_number',
                     'user__city',
                     'user__department__title',
                     'user__master__last_name',
                     'user__email',
                     )
    ordering_fields = ('user__first_name', 'user__last_name', 'user__master__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__district',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__department__title', 'user__facebook',
                       'user__vkontakte', 'value',)
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'], )
    def post_anket(self, request):
        if request.method == 'POST':
            keys = request.data.keys()
            if 'user_id' in keys and 'summit_id' in keys:
                user = CustomUser.objects.filter(id=request.data['user_id']).first()
                summit = Summit.objects.filter(id=request.data['summit_id']).first()
                if user:
                    if summit:
                        sa = SummitAnket.objects.filter(user=user)
                        sa = sa.filter(summit=summit).first()
                        visited = request.data.get('visited', None)
                        if sa:
                            if len(request.data['value']) > 0:
                                sa.value = request.data['value']
                            if len(request.data['description']) > 0:
                                sa.description = request.data['description']
                            if visited in (True, False):
                                sa.visited = visited
                            sa.save()
                            data = {"message": "Данные успешно измененны",
                                    'status': True}
                            if data['status'] and request.data.get('send_email', False):
                                email_data = {
                                    'anket_id': sa.id,
                                    'email': sa.user.email,
                                    'summit_name': str(sa.summit),
                                    'fullname': sa.user.fullname,
                                    'code': sa.code,
                                    'ticket': sa.ticket.url if sa.ticket else None
                                }
                                send_ticket.delay(email_data)
                        else:
                            visited = True if visited == True else False
                            if len(request.data['value']) > 0:
                                s = SummitAnket.objects.create(user=user, summit=summit, value=request.data['value'],
                                                               description=request.data['description'],
                                                               visited=visited)
                                if 'retards' in keys:
                                    if request.data['retards']:
                                        s.retards = request.data['retards']
                                        s.code = request.data['code']
                                    get_fields(s)
                                else:
                                    get_fields(s)
                            else:
                                s = SummitAnket.objects.create(user=user, summit=summit, visited=visited,
                                                               description=request.data['description'])
                                if 'retards' in keys:
                                    if request.data['retards']:
                                        s.retards = request.data['retards']
                                        s.code = request.data['code']
                                    get_fields(s)
                                else:
                                    get_fields(s)
                            data = {"message": "Данные успешно сохраненны",
                                    'status': True}
                            if data['status'] and request.data.get('send_email', False):
                                email_data = {
                                    'anket_id': s.id,
                                    'email': s.user.email,
                                    'summit_name': str(s.summit),
                                    'fullname': s.user.fullname,
                                    'code': s.code,
                                    'ticket': sa.ticket.url if sa.ticket else None
                                }
                                send_ticket.delay(email_data)
                    else:
                        data = {"message": "Такой саммит отсутствует",
                                'status': False}
                else:
                    data = {'message': "Такого пользователя не существует",
                            'status': False}
            else:
                data = {'message': "Некорректные данные",
                        'status': False}
        else:
            data = {'message': "Неправильный запрос",
                    'status': False}
        return Response(data)

    @detail_route(methods=['get'])
    def notes(self, request, pk=None):
        serializer = SummitAnketNoteSerializer
        anket = get_object_or_404(SummitAnket, pk=pk)
        queryset = anket.notes

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'])
    def create_note(self, request, pk=None):
        text = request.data['text']
        data = dict()
        data['text'] = text
        data['summit_anket'] = pk
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
        lesson = get_object_or_404(SummitLesson, pk=pk)
        anket = get_object_or_404(SummitAnket, pk=anket_id)

        lesson.viewers.add(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': True})

    @detail_route(methods=['post'])
    def del_viewer(self, request, pk=None):
        anket_id = request.data['anket_id']
        lesson = get_object_or_404(SummitLesson, pk=pk)
        anket = get_object_or_404(SummitAnket, pk=anket_id)

        lesson.viewers.remove(anket)

        return Response({'lesson': lesson.name, 'lesson_id': pk, 'anket_id': anket_id, 'checked': False})


class SummitAnketWithNotesViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.select_related('user', 'user__hierarchy', 'user__department', 'user__master'). \
        prefetch_related('user__divisions', 'notes')
    serializer_class = SummitAnketWithNotesSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('user',)


class SummitViewSet(viewsets.ModelViewSet):
    queryset = Summit.objects.prefetch_related('lessons').order_by('-start_date')
    serializer_class = SummitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('type',)
    permission_classes = (IsAuthenticated,)

    @detail_route(methods=['get'])
    def lessons(self, request, pk=None):
        serializer = SummitLessonSerializer
        summit = get_object_or_404(Summit, pk=pk)
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
        serializer = UserShortSerializer
        summit = get_object_or_404(Summit, pk=pk)
        queryset = summit.consultants

        serializer = serializer(queryset, many=True)

        return Response(serializer.data)

    @detail_route(methods=['post'], )
    def add_consultant(self, request, pk=None):
        user_id = request.data['user_id']
        summit = get_object_or_404(Summit, pk=pk)
        user = get_object_or_404(CustomUser, pk=user_id)
        summit.consultants.add(user)
        data = {'sumit_id': pk, 'consultant_id': user_id, 'action': 'added'}

        return Response(data, status=status.HTTP_201_CREATED)

    @detail_route(methods=['post'], )
    def del_consultant(self, request, pk=None):
        user_id = request.data['user_id']
        summit = get_object_or_404(Summit, pk=pk)
        user = get_object_or_404(CustomUser, pk=user_id)
        summit.consultants.remove(user)
        data = {'sumit_id': pk, 'consultant_id': user_id, 'action': 'removed'}

        return Response(data, status=status.HTTP_201_CREATED)


class SummitTypeForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitType.objects.prefetch_related('summits')
    serializer_class = SummitTypeForAppSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SummitAnketForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user').order_by('id')
    serializer_class = SummitAnketForAppSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('summit',)
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
    summit_id = filters_new.CharFilter(name="summit_ankets__summit__id")

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
