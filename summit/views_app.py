import logging
from datetime import datetime, timedelta

from django.db.models import ExpressionWrapper, F, IntegerField
from django.utils.translation import ugettext_lazy as _
from rest_framework import mixins, viewsets, exceptions, status, filters
from rest_framework.decorators import list_route, api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from common.filters import FieldSearchFilter
from common.views_mixins import ModelWithoutDeleteViewSet
from .models import (
    SummitType, SummitAnket, AnketStatus, Summit, SummitVisitorLocation, SummitAttend, SummitEventTable,
    AnketPasses)
from .permissions import HasAPIAccess
from .serializers import (
    SummitTypeForAppSerializer, SummitAnketForAppSerializer, SummitProfileTreeForAppSerializer,
    SummitVisitorLocationSerializer, SummitAnketCodeSerializer, SummitAttendSerializer,
    SummitAcceptMobileCodeSerializer, AnketActiveStatusSerializer, SummitEventTableSerializer)

logger = logging.getLogger(__name__)


class SummitTypeForAppViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = SummitType.objects.prefetch_related('summits')
    serializer_class = SummitTypeForAppSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class SummitAnketForAppViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = SummitAnket.objects.select_related('user', 'master__hierarchy', 'status').order_by('id')
    serializer_class = SummitAnketForAppSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (HasAPIAccess,)
    pagination_class = None
    filter_fields = ('summit',)

    @list_route(methods=['GET'])
    def by_reg_code(self, request):
        reg_code = request.query_params.get('reg_code')
        code_error_message = _('Невозможно получить объект. Передан некорректный регистрационный код')

        try:
            int_reg_code = int('0x' + reg_code, 0)
            visitor_id = int(str(int_reg_code)[:-4])
        except ValueError:
            raise exceptions.ValidationError(code_error_message)

        visitor = get_object_or_404(SummitAnket, pk=visitor_id)

        if visitor.reg_code != reg_code:
            raise exceptions.ValidationError(code_error_message)

        AnketStatus.objects.get_or_create(
            anket=visitor, defaults={'reg_code_requested': True,
                                     'reg_code_requested_date': datetime.now()})
        # visitor.ticket_status = SummitAnket.GIVEN
        # visitor.save()

        visitor = self.get_serializer(visitor)
        return Response(visitor.data)

    @list_route(methods=['GET'])
    def by_reg_date(self, request):
        from_date = request.query_params.get('from_date', datetime.now().date() - timedelta(days=1))
        to_date = request.query_params.get('to_date', datetime.now().date() - timedelta(days=1))

        if from_date > to_date:
            raise exceptions.ValidationError('Некорректно заданный временной интвервал. ')

        ankets = SummitAnket.objects.filter(
            status__reg_code_requested_date__date__range=[from_date, to_date]).order_by(
            'status__reg_code_requested_date')
        ankets = self.serializer_class(ankets, many=True)
        return Response(ankets.data)


@api_view(['GET'])
def app_request_count(request, summit_id):
    profiles = SummitAnket.objects.filter(summit_id=summit_id).values_list(
        'status__reg_code_requested', flat=True)
    total = len(profiles)
    requested = len(list(filter(lambda p: p, profiles)))
    return Response({'total': total, 'requested': requested})


class SummitProfileTreeForAppListView(mixins.ListModelMixin, GenericAPIView):
    serializer_class = SummitProfileTreeForAppSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated,)

    filter_backends = (
        FieldSearchFilter,
    )

    field_search_fields = {
        'search_fio': ('last_name', 'first_name', 'middle_name', 'search_name'),
    }

    def dispatch(self, request, *args, **kwargs):
        return super(SummitProfileTreeForAppListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.summit = get_object_or_404(Summit, pk=kwargs.get('summit_id', None))
        self.master_id = kwargs.get('master_id', None)
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        serializer = self.get_serializer(queryset, many=True)
        profiles = serializer.data
        ids = {p['id'] for p in profiles}

        locations = SummitVisitorLocation.objects.filter(visitor__in=ids)
        date_time = request.query_params.get('date_time', '')
        interval = int(request.query_params.get('interval', 5))
        try:
            date_time = datetime.strptime(date_time.replace('T', ' '), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            end_date = datetime.now()
            start_date = end_date - timedelta(minutes=2 * interval)
        else:
            start_date = date_time - timedelta(minutes=interval)
            end_date = date_time + timedelta(minutes=interval)
        locations = locations.filter(date_time__range=(start_date, end_date)).values(
            'visitor_id', 'date_time', 'longitude', 'latitude', 'type')
        for p in profiles:
            p['visitor_locations'] = None
            for l in locations:
                if l['visitor_id'] == p['id']:
                    p['visitor_locations'] = l
                    break

        return Response({
            'profiles': profiles,
        })

    def annotate_queryset(self, qs):
        return qs.select_related('status').base_queryset().annotate_full_name().annotate(
            diff=ExpressionWrapper(F('user__rght') - F('user__lft'), output_field=IntegerField()),
        ).order_by('-hierarchy__level', 'last_name', 'first_name', 'middle_name')

    def get_queryset(self):
        is_consultant_or_high = self.request.user.is_summit_consultant_or_high(self.summit)
        if self.master_id is not None:
            if is_consultant_or_high:
                return self.annotate_queryset(self.summit.ankets.filter(user__master_id=self.master_id))
            return self.annotate_queryset(self.summit.ankets.filter(
                user__master_id=self.master_id
            ))
        elif is_consultant_or_high:
            return self.annotate_queryset(self.summit.ankets.filter(user__level=0))
        else:
            return self.annotate_queryset(self.summit.ankets.filter(user__master_id=self.request.user.id))


class SummitVisitorLocationViewSet(viewsets.ModelViewSet):
    serializer_class = SummitVisitorLocationSerializer
    queryset = SummitVisitorLocation.objects.all().prefetch_related('visitor')
    pagination_class = None
    permission_classes = (HasAPIAccess,)

    @list_route(methods=['POST'])
    def post(self, request):
        if not request.data.get('data'):
            logger.warning({
                'user': getattr(request, 'real_user', request.user).id,
                'message': _('Невозможно создать запись, поле {data} не переданно')
            })
            raise exceptions.ValidationError(_('Невозможно создать запись, поле {data} не переданно'))
        data = request.data.get('data')
        visitor = get_object_or_404(SummitAnket, pk=request.data.get('visitor_id'))

        for chunk in data:
            SummitVisitorLocation.objects.get_or_create(
                visitor=visitor,
                date_time=chunk.get('date_time', datetime.now()),
                defaults={
                    'longitude': chunk.get('longitude', 0),
                    'latitude': chunk.get('latitude', 0),
                    'type': chunk.get('type', 1)
                })

        return Response({'message': 'Successful created'}, status=status.HTTP_201_CREATED)

    @list_route(methods=['GET'])
    def get_location(self, request):
        anket_id = request.query_params.get('visitor_id')
        date_time = request.query_params.get('date_time')
        visitor_location = self.queryset.filter(visitor_id=anket_id, date_time__gte=date_time).order_by(
            'date_time').first()
        visitor_location = self.serializer_class(visitor_location)

        return Response(visitor_location.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def location_by_interval(self, request):
        date_time = request.query_params.get('date_time')
        date_format = '%Y-%m-%d %H:%M:%S'
        try:
            date_time = datetime.strptime(date_time.replace('T', ' '), date_format)
        except ValueError:
            raise exceptions.ValidationError(
                'Не верный формат даты. Передайте дату в формате date %s' % date_format)

        interval = int(request.query_params.get('interval', 0))
        start_date = date_time - timedelta(minutes=interval)
        end_date = date_time + timedelta(minutes=interval)

        locations = self.queryset.filter(date_time__range=(start_date, end_date))
        locations = self.serializer_class(locations, many=True)

        return Response(locations.data, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def location_by_date(self, request):
        anket_id = request.query_params.get('visitor_id')
        date = request.query_params.get('date')
        visitor_locations = self.queryset.filter(visitor_id=anket_id, date_time__date=date)
        visitor_locations = self.serializer_class(visitor_locations, many=True)

        return Response(visitor_locations.data, status=status.HTTP_200_OK)


class SummitAttendViewSet(ModelWithoutDeleteViewSet):
    queryset = SummitAttend.objects.prefetch_related('anket')
    serializer_class = SummitAnketCodeSerializer
    serializer_list_class = SummitAttendSerializer
    permission_classes = (HasAPIAccess,)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_list_class
        return self.serializer_class

    @list_route(methods=['POST', 'GET'])
    def confirm_attend(self, request):
        code = request.data.get('code')
        date = request.data.get('date')
        anket = get_object_or_404(SummitAnket, code=code)
        self.validate_data(request.data)
        SummitAttend.objects.create(anket=anket, date=date)

        return Response({'message': 'Attend have been successful confirmed'}, status=status.HTTP_201_CREATED)

    @staticmethod
    def validate_data(data):
        anket = get_object_or_404(SummitAnket, code=data.get('code'))
        date_today = datetime.now().date()
        if SummitAttend.objects.filter(anket_id=anket.id, date=date_today).exists():
            raise exceptions.ValidationError(
                _('Запись о присутствии этой анкеты за сегоднящней день уже существует'))

    @list_route(methods=['GET'], serializer_class=SummitAcceptMobileCodeSerializer)
    def accept_mobile_code(self, request):
        code = request.query_params.get('code', '')
        anket = get_object_or_404(SummitAnket, code=code)
        AnketStatus.objects.get_or_create(
            anket=anket, defaults={'reg_code_requested': True,
                                   'reg_code_requested_date': datetime.now()})

        if anket.status.active:
            SummitAttend.objects.get_or_create(anket=anket, date=datetime.now().date())
            AnketPasses.objects.create(anket=anket)

        anket = self.serializer_class(anket)
        return Response(anket.data)

    @list_route(methods=['POST'], serializer_class=AnketActiveStatusSerializer,
                permission_classes=(IsAuthenticated,))
    def anket_active_status(self, request):
        active = request.data.get('active', 1)
        anket_id = request.data.get('anket_id', None)
        anket = get_object_or_404(SummitAnket, pk=anket_id)
        AnketStatus.objects.get_or_create(anket=anket)

        if active:
            anket.status.active = True
        if not active:
            anket.status.active = False
        anket.status.save()

        return Response({'message': _('Статус анкеты пользователя {%s} успешно изменен.') % anket.fullname,
                         'active': '%s' % anket.status.active}, status=status.HTTP_200_OK)


class SummitEventTableViewSet(viewsets.ModelViewSet):
    queryset = SummitEventTable.objects.all()
    serializer_class = SummitEventTableSerializer
    permission_classes = (HasAPIAccess,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('summit',)
    pagination_class = None
