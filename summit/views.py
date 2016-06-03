# -*- coding: utf-8
from models import Summit, SummitAnket, SummitType
from account.models import CustomUser
from serializers import SummitAnketSerializer, SummitSerializer, SummitTypeSerializer, SummitUnregisterUserSerializer
from rest_framework import viewsets, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from account.serializers import UserSerializer
import rest_framework_filters as filters_new
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class SummitPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 30

    def get_paginated_response(self, data):
        return Response({
            'links': {'next': self.get_next_link(),
                      'previous': self.get_previous_link()
                      },
            'count': self.page.paginator.count,
            'results': data
        })


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
                     )
    search_fields = ('user__first_name',
                     'user__last_name',
                     'user__middle_name',
                     'user__hierarchy__title',
                     'user__phone_number',
                     'user__city',
                     'user__department__title',
                     )
    ordering_fields = ('user__first_name', 'user__last_name',
                       'user__middle_name', 'user__born_date', 'user__country',
                       'user__region', 'user__city', 'user__disrict',
                       'user__address', 'user__skype', 'user__phone_number',
                       'user__email', 'user__hierarchy__level',
                       'user__department__title', 'user__facebook',
                       'user__vkontakte', 'value',)
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'],)
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
                            data = {"message": u"Данные успешно измененны",
                                    'status': True}
                        else:
                            if len(request.data['value']) > 0:
                                SummitAnket.objects.create(user=user, summit=summit, value=request.data['value'], description=request.data['description'])
                            else:
                                SummitAnket.objects.create(user=user, summit=summit, description=request.data['description'])
                            data = {"message": u"Данные успешно сохраненны",
                                    'status': True}
                    else:
                        data = {"message": u"Такой саммит отсутствует",
                                'status': False}
                else:
                    data = {'message': u"Такого полльзователя не существует",
                            'status': False}
            else:
                data = {'message': u"Некорректные данные",
                        'status': False}
        else:
            data = {'message': u"Неправильный запрос",
                    'status': False}
        return Response(data)

    @list_route(methods=['post'],)
    def delete_anket(self, request):
        if request.method == 'POST':
            sa = SummitAnket.objects.filter(id=request.data['id']).first()
            if sa:
                sa.delete()
                data = {"message": u"Анкета удаленна",
                        'status': True}
            else:
                data = {"message": u"Анкеты не существует",
                        'status': False}
            return Response(data)


class SummitViewSet(viewsets.ModelViewSet):
    queryset = Summit.objects.all().order_by('start_date')
    serializer_class = SummitSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('type',
                     )
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['post'],)
    def delete_summit(self, request):
        if request.method == 'POST':
            summit = Summit.objects.filter(id=request.data['id']).first()
            if summit:
                summit.delete()
                data = {"message": u"Анкета удаленна",
                        'status': True}
            else:
                data = {"message": u"Анкеты не существует",
                        'status': False}
            return Response(data)

    @list_route(methods=['post'],)
    def update_summit(self, request):
        if request.method == "POST":
            summit = Summit.objects.filter(id=request.data['id']).first()
            if summit:
                for key in request.data:
                    if key == 'start_date':
                        summit.start_date = request.data['start_date']
                        response_data = {'message': u'Данные успешно измененны'}
                    elif key == 'end_date':
                        summit.end_date = request.data['end_date']
                        response_data = {'message': u'Данные успешно измененны'}
                    elif key == 'title':
                        summit.title = request.data['title']
                        response_data = {'message': u'Данные успешно измененны'}
                    elif key == 'description':
                        summit.description = request.data['description']
                        response_data = {'message': u'Данные успешно измененны'}
                    else:
                        response_data = {'message': u'Некорректные данные'}
            else:
                response_data = {'message': u'Такого саммита не существует'}
        else:
            response_data = {'message': u'Неправильный запрос'}
        return Response(response_data)

    @list_route(methods=['get'],)
    def user(self, request):
        if 'id' in request.GET.keys():
            user = CustomUser.objects.filter(id=request.GET['id']).first()
            if user:
                summits = Summit.objects.exclude(ankets__user=user)
                serializer = self.get_serializer(summits, many=True)
                return Response(serializer.data)
            else:
                data = {'message': u'Такого пользователя не существует',
                        'status': False}
        else:
            data = {'message': u'Введите нужный id пользователя',
                    'status': False}
        if data:
            return Response(data)


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
    pagination_class = None
    filter_backends = (filters.SearchFilter,
                       filters.DjangoFilterBackend,)
    permission_classes = (IsAuthenticated,)
    filter_class = SummitUnregisterFilter
    search_fields = ('first_name', 'last_name', 'middle_name',
                     'country', 'region', 'city', 'district',
                     'address', 'email', )
