# -*- coding: utf-8
from __future__ import unicode_literals

import rest_framework_filters as filters_new
from rest_framework import status
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.decorators import list_route, detail_route
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from account.models import CustomUser
from navigation.models import user_table, user_summit_table
from .models import Summit, SummitAnket, SummitType, SummitAnketNote
from .resources import get_fields
from .resources import make_table
from .serializers import SummitAnketSerializer, SummitSerializer, SummitTypeSerializer, SummitUnregisterUserSerializer, \
    NewSummitAnketSerializer, SummitAnketNoteSerializer, SummitAnketWithNotesSerializer, SummitLessonSerializer


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


class NewSummitAnketViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.select_related('user', 'user__hierarchy', 'user__department', 'user__master'). \
        prefetch_related('user__divisions')
    serializer_class = NewSummitAnketSerializer
    pagination_class = SummitPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       )
    filter_fields = ('user',
                     'summit',
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
                    sa = SummitAnket.objects.filter(user=user)
                    if summit:
                        sa = sa.filter(summit=summit).first()
                        if sa:
                            if len(request.data['value']) > 0:
                                sa.value = request.data['value']
                            if len(request.data['description']) > 0:
                                sa.description = request.data['description']
                            sa.save()
                            data = {"message": "Данные успешно измененны",
                                    'status': True}
                        else:
                            if len(request.data['value']) > 0:
                                s = SummitAnket.objects.create(user=user, summit=summit, value=request.data['value'],
                                                               description=request.data['description'])
                                if 'retards' in keys:
                                    if request.data['retards']:
                                        s.retards = request.data['retards']
                                        s.code = request.data['code']
                                    get_fields(s)
                                else:
                                    get_fields(s)
                            else:
                                s = SummitAnket.objects.create(user=user, summit=summit,
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
                    else:
                        data = {"message": "Такой саммит отсутствует",
                                'status': False}
                else:
                    data = {'message': "Такого полльзователя не существует",
                            'status': False}
            else:
                data = {'message': "Некорректные данные",
                        'status': False}
        else:
            data = {'message': "Неправильный запрос",
                    'status': False}
        return Response(data)

    @list_route(methods=['post'], )
    def delete_anket(self, request):
        if request.method == 'POST':
            sa = SummitAnket.objects.filter(id=request.data['id']).first()
            if sa:
                sa.delete()
                data = {"message": "Анкета удаленна",
                        'status': True}
            else:
                data = {"message": "Анкеты не существует",
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


class SummitAnketWithNotesViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.select_related('user', 'user__hierarchy', 'user__department', 'user__master'). \
        prefetch_related('user__divisions', 'notes')
    serializer_class = SummitAnketWithNotesSerializer
    pagination_class = None
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('user',)


class SummitAnketViewSet(viewsets.ModelViewSet):
    queryset = SummitAnket.objects.all()
    serializer_class = SummitAnketSerializer
    pagination_class = SummitPagination
    filter_backends = (filters.DjangoFilterBackend,
                       filters.SearchFilter,
                       filters.OrderingFilter,
                       )
    filter_fields = ('user',
                     'summit',
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
                    sa = SummitAnket.objects.filter(user=user)
                    if summit:
                        sa = sa.filter(summit=summit).first()
                        if sa:
                            if len(request.data['value']) > 0:
                                sa.value = request.data['value']
                            if len(request.data['description']) > 0:
                                sa.description = request.data['description']
                            sa.save()
                            data = {"message": "Данные успешно измененны",
                                    'status': True}
                        else:
                            if len(request.data['value']) > 0:
                                s = SummitAnket.objects.create(user=user, summit=summit, value=request.data['value'],
                                                               description=request.data['description'])
                                if 'retards' in keys:
                                    if request.data['retards']:
                                        s.retards = request.data['retards']
                                        s.code = request.data['code']
                                    get_fields(s)
                                else:
                                    get_fields(s)
                            else:
                                s = SummitAnket.objects.create(user=user, summit=summit,
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
                    else:
                        data = {"message": "Такой саммит отсутствует",
                                'status': False}
                else:
                    data = {'message': "Такого полльзователя не существует",
                            'status': False}
            else:
                data = {'message': "Некорректные данные",
                        'status': False}
        else:
            data = {'message': "Неправильный запрос",
                    'status': False}
        return Response(data)

    @list_route(methods=['post'], )
    def delete_anket(self, request):
        if request.method == 'POST':
            sa = SummitAnket.objects.filter(id=request.data['id']).first()
            if sa:
                sa.delete()
                data = {"message": "Анкета удаленна",
                        'status': True}
            else:
                data = {"message": "Анкеты не существует",
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


class SummitViewSet(viewsets.ModelViewSet):
    queryset = Summit.objects.prefetch_related('lessons').order_by('start_date')
    serializer_class = SummitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('type',
                     )
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'], )
    def delete_summit(self, request):
        if request.method == 'POST':
            summit = Summit.objects.filter(id=request.data['id']).first()
            if summit:
                summit.delete()
                data = {"message": "Анкета удаленна",
                        'status': True}
            else:
                data = {"message": "Анкеты не существует",
                        'status': False}
            return Response(data)

    @list_route(methods=['post'], )
    def update_summit(self, request):
        if request.method == "POST":
            summit = Summit.objects.filter(id=request.data['id']).first()
            if summit:
                for key in request.data:
                    if key == 'start_date':
                        summit.start_date = request.data['start_date']
                        response_data = {'message': 'Данные успешно измененны'}
                    elif key == 'end_date':
                        summit.end_date = request.data['end_date']
                        response_data = {'message': 'Данные успешно измененны'}
                    elif key == 'title':
                        summit.title = request.data['title']
                        response_data = {'message': 'Данные успешно измененны'}
                    elif key == 'description':
                        summit.description = request.data['description']
                        response_data = {'message': 'Данные успешно измененны'}
                    else:
                        response_data = {'message': 'Некорректные данные'}
            else:
                response_data = {'message': 'Такого саммита не существует'}
        else:
            response_data = {'message': 'Неправильный запрос'}
        return Response(response_data)

    @list_route(methods=['get'], )
    def user(self, request):
        if 'id' in request.GET.keys():
            user = CustomUser.objects.filter(id=request.GET['id']).first()
            if user:
                summits = Summit.objects.exclude(ankets__user=user)
                serializer = self.get_serializer(summits, many=True)
                return Response(serializer.data)
            else:
                data = {'message': 'Такого пользователя не существует',
                        'status': False}
        else:
            data = {'message': 'Введите нужный id пользователя',
                    'status': False}
        if data:
            return Response(data)

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


class SummitTypeViewSet(viewsets.ModelViewSet):
    queryset = SummitType.objects.all()
    serializer_class = SummitTypeSerializer
    permission_classes = (IsAuthenticated,)


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
    search_fields = ('first_name', 'last_name', 'middle_name',
                     # 'country', 'region', 'city', 'district',
                     # 'address', 'email',
                     )


class SummitAnketNoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SummitAnketNote.objects.all()
    serializer_class = SummitAnketNoteSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('summit_anket',)
    permission_classes = (IsAuthenticated,)


@api_view(['GET'])
def generate(request):
    try:
        make_table()
        r = "Все ок, чувак"
    except:
        r = "Что-то пошло пиздец как не так"
    return Response(r)
